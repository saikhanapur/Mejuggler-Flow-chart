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
    
    async def process_visual_pdf(self, pdf_bytes: bytes, filename: str) -> Dict:
        """
        Process visual/scanned PDF using Claude Vision API (Native Anthropic SDK).
        Pages are processed in batches of 5.  Documents over 50 pages scan every
        other page and surface a visible truncation_warning in the returned dict.
        Returns: {"text": str, "truncation_warning": str|None, "pages_processed": int, "total_pages": int}
        """
        try:
            logger.info(f"Scanning visual PDF: {filename}")

            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(pdf_reader.pages)
            logger.info(f"Document has {total_pages} total pages")

            truncation_warning = None
            MAX_SYNC_PAGES = 10  # Cap for synchronous processing within gateway timeout

            if total_pages > 50:
                # Very large doc: every other page, capped at MAX_SYNC_PAGES
                pages_to_process = list(range(1, total_pages + 1, 2))[:MAX_SYNC_PAGES]
                truncation_warning = (
                    f"Partial coverage: document has {total_pages} pages. "
                    f"Every other page was scanned ({len(pages_to_process)} pages processed). "
                    "Content on skipped pages may not appear in the flowchart."
                )
            elif total_pages > MAX_SYNC_PAGES:
                # Medium doc: first MAX_SYNC_PAGES pages
                pages_to_process = list(range(1, MAX_SYNC_PAGES + 1))
                truncation_warning = (
                    f"Document has {total_pages} pages. "
                    f"First {MAX_SYNC_PAGES} pages were processed to stay within time limits. "
                    "Re-upload pages 11+ as a separate document to capture remaining content."
                )
            else:
                pages_to_process = list(range(1, total_pages + 1))

            for batch_start in range(0, len(pages_to_process), batch_size):
                batch = pages_to_process[batch_start:batch_start + batch_size]
                first_in_batch = batch[0]
                last_in_batch = batch[-1]
                logger.info(f"Converting batch pages {first_in_batch}-{last_in_batch} to images")

                images = convert_from_bytes(
                    pdf_bytes,
                    first_page=first_in_batch,
                    last_page=last_in_batch,
                    dpi=150
                )

                for page_num, image in zip(batch, images):
                    logger.info(f"Analyzing page {page_num}/{total_pages} with Claude Vision...")

                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG", optimize=True, quality=85)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()

                    prompt = (
                        f"You are an expert at analyzing business process flowcharts and SOPs.\n\n"
                        f"Analyze this flowchart document (page {page_num}) and extract EVERYTHING with extreme precision:\n\n"
                        "## CRITICAL INSTRUCTIONS:\n"
                        "Extract ALL information - treat this like a life-or-death emergency procedure where missing ANY detail could be catastrophic.\n\n"
                        "## SECTION 1: PROCESS STRUCTURE\n"
                        "For each shape/node you see:\n"
                        "- Exact text inside the shape\n"
                        "- Shape type (rectangle, diamond, oval, etc.)\n"
                        "- Shape color (blue, yellow, green, red, grey, white, etc.)\n"
                        "- Position in the flow (which swim lane, sequence number)\n"
                        "- What it connects TO (list all arrows going out)\n"
                        "- What connects to IT (list all arrows coming in)\n\n"
                        "## SECTION 2: DECISION POINTS\n"
                        "For EVERY diamond shape:\n"
                        "- Exact decision question\n"
                        "- YES branch destination\n"
                        "- NO branch destination\n"
                        "- Any conditions or criteria mentioned\n\n"
                        "## SECTION 3: SWIM LANES / COLUMNS\n"
                        "Identify all vertical or horizontal sections:\n"
                        "- Section names (e.g., 'Onshore Actions', 'Offshore Actions')\n"
                        "- Which steps belong to which section\n"
                        "- Any role labels (Supervisor, Patrol Officer, etc.)\n\n"
                        "## SECTION 4: CONTACTS & REFERENCES\n"
                        "Extract EVERY single: Name, phone, email, system names, document references, URLs\n\n"
                        "## SECTION 5: TIMINGS & DEADLINES\n"
                        "Extract ALL time-related information: durations, frequencies, deadlines, sequences\n\n"
                        "## SECTION 6: REFERENCE BOXES\n"
                        "Look for yellow/highlighted boxes: message templates, email scripts, call scripts, quick reference guides\n\n"
                        "## SECTION 7: PARALLEL PROCESSES\n"
                        "Identify steps that happen simultaneously vs sequentially\n\n"
                        "## OUTPUT FORMAT:\n"
                        "SWIM LANES: [List all swim lanes]\n"
                        "PROCESS STEPS (in order): Step N: [Exact text] (Shape, Color, Lane) -> Connects to: [steps]\n"
                        "DECISION POINTS: Decision N: [Exact question] - YES -> [dest] - NO -> [dest]\n"
                        "CONTACTS: [Name]: [Phone] / [Email]\n"
                        "TIMINGS: [Time requirement]\n"
                        "REFERENCES: [Document/template name]\n"
                        "MESSAGE TEMPLATES: [Copy any templates word-for-word]\n\n"
                        "Be EXTREMELY thorough. Missing information = failure."
                    )

                    message = client.messages.create(
                        model="claude-4-sonnet-20250514",
                        max_tokens=4000,
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": img_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }]
                    )

                    page_text = message.content[0].text
                    all_extracted_text.append(f"=== PAGE {page_num} ===\n{page_text}\n")
                    logger.info(f"Page {page_num} extracted: {len(page_text)} characters")

            combined_text = "\n\n".join(all_extracted_text)
            logger.info(f"Vision extraction complete: {len(combined_text)} total characters from {len(pages_to_process)} pages")

            return {
                "text": combined_text,
                "truncation_warning": truncation_warning,
                "pages_processed": len(pages_to_process),
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Vision processing failed: {e}", exc_info=True)
            logger.info("Falling back to text extraction...")
            return {
                "text": self.extract_text_from_pdf(pdf_bytes),
                "truncation_warning": None,
                "pages_processed": 0,
                "total_pages": 0,
            }

    
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
                    vision_result = await self.process_visual_pdf(file_bytes, filename)
                    return {
                        "text": vision_result["text"],
                        "method": "vision",
                        "confidence": confidence,
                        "pages_processed": vision_result["pages_processed"],
                        "total_pages": vision_result["total_pages"],
                        "truncation_warning": vision_result["truncation_warning"],
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
        """Process standalone image files with native Anthropic vision"""
        try:
            # Convert to base64
            img_base64 = base64.b64encode(image_bytes).decode()
            
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = """Extract ALL information from this process document/flowchart image.
Include: all text, process steps, decisions, contacts, timings, references, swim lanes, and structural information.
Be extremely thorough - extract EVERYTHING you see."""
            
            # Call Claude Vision API
            message = client.messages.create(
                model="claude-4-sonnet-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
