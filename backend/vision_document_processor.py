"""
Vision-Enhanced Document Processor
Handles both text-based and visual PDFs using hybrid approach
Uses native Anthropic API for vision processing
"""

import io
import base64
import logging
from typing import Dict, Tuple
from PIL import Image
import pypdf
from pdf2image import convert_from_bytes
import anthropic

logger = logging.getLogger(__name__)

class VisionDocumentProcessor:
    """
    Hybrid document processor that intelligently routes between:
    - Text extraction (for text-based PDFs)
    - Vision AI (for visual/scanned PDFs)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def detect_pdf_type(self, pdf_bytes: bytes) -> Tuple[bool, float]:
        """
        Detect if PDF is text-based or image-based
        
        Returns:
            (is_text_based, confidence)
            - is_text_based: True if PDF has extractable text WITHOUT visual elements
            - confidence: 0.0-1.0 confidence score
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            
            # Check first 3 pages (or all if fewer)
            pages_to_check = min(3, len(pdf_reader.pages))
            total_text_length = 0
            total_images = 0
            
            for i in range(pages_to_check):
                page = pdf_reader.pages[i]
                text = page.extract_text()
                total_text_length += len(text.strip())
                
                # Count images/visual elements
                try:
                    if '/XObject' in page['/Resources']:
                        xobject = page['/Resources']['/XObject'].get_object()
                        images = [k for k in xobject if xobject[k]['/Subtype'] == '/Image']
                        total_images += len(images)
                except:
                    pass
            
            avg_text_per_page = total_text_length / pages_to_check
            avg_images_per_page = total_images / pages_to_check
            
            # IMPROVED HEURISTIC:
            # If PDF has many images (>50 per page), it's likely a visual flowchart
            # Even if it has embedded text
            if avg_images_per_page > 50:
                logger.info(f"🖼️ Visual flowchart PDF detected: {avg_images_per_page:.0f} images/page, {avg_text_per_page:.0f} chars/page")
                return False, 0.9
            
            # If it has substantial text but few images, it's text-based
            if avg_text_per_page > 500 and avg_images_per_page < 10:
                confidence = min(1.0, avg_text_per_page / 1000)
                logger.info(f"📄 Text-based PDF detected: {avg_text_per_page:.0f} chars/page, {avg_images_per_page:.0f} images/page (confidence: {confidence:.2f})")
                return True, confidence
            
            # If it has moderate text and moderate images, prefer vision for accuracy
            if avg_images_per_page > 10:
                logger.info(f"🖼️ Visual PDF with embedded text: {avg_images_per_page:.0f} images/page, {avg_text_per_page:.0f} chars/page")
                return False, 0.8
            
            # Low text, low images - default to vision
            if avg_text_per_page < 100:
                logger.info(f"🖼️ Scanned/Visual PDF detected: {avg_text_per_page:.0f} chars/page")
                return False, 0.7
            
            # Moderate text, few images - use text extraction
            logger.info(f"📄 Text document detected: {avg_text_per_page:.0f} chars/page, {avg_images_per_page:.0f} images/page")
            return True, 0.7
                
        except Exception as e:
            logger.error(f"Error detecting PDF type: {e}")
            # Default to visual processing if detection fails (better safe than sorry)
            return False, 0.5
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Traditional text extraction for text-based PDFs"""
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"✅ Extracted {len(text)} characters via text extraction")
            return text
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def process_visual_pdf(self, pdf_bytes: bytes, filename: str) -> str:
        """
        Process visual/scanned PDF using Claude Vision
        Converts PDF pages to images and analyzes with vision model
        """
        try:
            logger.info(f"🔍 Processing visual PDF: {filename}")
            
            # Convert PDF to images (first 5 pages to avoid token limits)
            images = convert_from_bytes(
                pdf_bytes,
                first_page=1,
                last_page=min(5, 10),  # Limit to 5 pages for now
                dpi=150  # Balance between quality and size
            )
            
            logger.info(f"📸 Converted {len(images)} pages to images")
            
            # Process each page with Claude Vision
            all_extracted_text = []
            
            for idx, image in enumerate(images, 1):
                logger.info(f"🤖 Analyzing page {idx}/{len(images)} with Claude Vision...")
                
                # Convert PIL Image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG", optimize=True, quality=85)
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Create vision chat
                chat = LlmChat(
                    api_key=self.api_key,
                    session_id=f"vision_page_{idx}",
                    system_message="You are an expert at analyzing flowcharts and SOPs. Extract ALL text, structure, and process information from this document image."
                )
                
                # Construct vision prompt
                prompt = f"""Analyze this SOP/flowchart document (page {idx}):

Extract EVERYTHING you see:
1. All text content (titles, steps, descriptions, annotations)
2. Flowchart structure:
   - Shapes (rectangles, diamonds, ovals) and their text
   - Decision points (diamond shapes) with YES/NO branches
   - Connections between nodes (arrows, flow direction)
   - Color coding if visible (green, yellow, red boxes)
3. Important details:
   - Names, phone numbers, email addresses
   - Timings, deadlines, durations
   - System names, URLs, links
   - Instructions in "yellow boxes" or annotations
4. Process flow:
   - Sequential steps
   - Parallel processes
   - Conditional branches
   - Loops or iterations

Preserve the logical structure and relationships. Include ALL information - nothing should be missed.

Output as clear, structured text that preserves the process flow."""

                # Send message with image
                response = await chat.send_message(UserMessage(
                    text=prompt,
                    image_data=img_base64,
                    image_format="png"
                ))
                
                page_text = response.text
                all_extracted_text.append(f"=== PAGE {idx} ===\n{page_text}\n")
                logger.info(f"✅ Page {idx} extracted: {len(page_text)} characters")
            
            # Combine all pages
            combined_text = "\n\n".join(all_extracted_text)
            logger.info(f"✅ Vision extraction complete: {len(combined_text)} total characters")
            
            return combined_text
            
        except Exception as e:
            logger.error(f"❌ Vision processing failed: {e}", exc_info=True)
            # Fallback to text extraction
            logger.info("⚠️ Falling back to text extraction...")
            return self.extract_text_from_pdf(pdf_bytes)
    
    async def process_document(
        self, 
        file_bytes: bytes, 
        filename: str,
        force_vision: bool = False
    ) -> Dict[str, any]:
        """
        Main entry point: Hybrid document processing
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            force_vision: If True, force vision processing regardless of detection
        
        Returns:
            {
                "text": extracted text,
                "method": "text" or "vision",
                "confidence": detection confidence
            }
        """
        try:
            # Detect document type
            if filename.lower().endswith('.pdf'):
                is_text_based, confidence = self.detect_pdf_type(file_bytes)
                
                if force_vision or not is_text_based:
                    # Use vision processing
                    text = await self.process_visual_pdf(file_bytes, filename)
                    return {
                        "text": text,
                        "method": "vision",
                        "confidence": confidence,
                        "pages_processed": text.count("=== PAGE")
                    }
                else:
                    # Use text extraction
                    text = self.extract_text_from_pdf(file_bytes)
                    return {
                        "text": text,
                        "method": "text",
                        "confidence": confidence
                    }
            else:
                # Non-PDF files - use existing logic
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    # For images, use vision
                    logger.info("🖼️ Image file - using vision processing")
                    text = await self._process_image_file(file_bytes)
                    return {
                        "text": text,
                        "method": "vision",
                        "confidence": 1.0
                    }
                else:
                    # Plain text files
                    text = file_bytes.decode('utf-8')
                    return {
                        "text": text,
                        "method": "text",
                        "confidence": 1.0
                    }
                    
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}", exc_info=True)
            raise
    
    async def _process_image_file(self, image_bytes: bytes) -> str:
        """Process standalone image files with vision"""
        try:
            # Convert to base64
            img_base64 = base64.b64encode(image_bytes).decode()
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id="vision_image",
                system_message="You are an expert at analyzing flowcharts and process documents."
            )
            
            prompt = """Extract all information from this process document/flowchart image.
Include all text, process steps, decisions, contacts, and structural information."""
            
            response = await chat.send_message(UserMessage(
                text=prompt,
                image_data=img_base64,
                image_format="png"
            ))
            
            return response.text
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
