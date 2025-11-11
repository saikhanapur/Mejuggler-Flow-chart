import React from 'react';

const EmergencyContacts = ({ contacts }) => {
  if (!contacts || Object.keys(contacts).length === 0) {
    return null;
  }

  // Helper to check if contact is hierarchical structure
  const isHierarchical = (contact) => {
    return typeof contact === 'object' && contact !== null && 'main' in contact;
  };

  return (
    <div className="mt-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-8 shadow-xl">
      <h3 className="font-bold text-blue-900 mb-6 text-2xl flex items-center gap-3">
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
        Emergency Contacts Quick Reference
      </h3>
      <div className="grid grid-cols-3 gap-6">
        {Object.entries(contacts).map(([name, contact], idx) => {
          const hierarchical = isHierarchical(contact);
          
          return (
            <div key={idx} className="bg-white/70 rounded-lg p-5 border border-blue-200 hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-blue-900 mb-3">{name}</h4>
              
              {hierarchical ? (
                // Hierarchical contact display
                <div className="text-sm text-blue-800 space-y-2">
                  {/* Main phone number */}
                  <div className="font-mono font-medium text-blue-900">
                    {contact.main}
                  </div>
                  
                  {/* Extension */}
                  {contact.extension && (
                    <div className="flex items-center gap-2 text-xs text-blue-700 bg-blue-100 px-2 py-1 rounded">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Extension: {contact.extension}
                    </div>
                  )}
                  
                  {/* Options */}
                  {contact.options && contact.options.length > 0 && (
                    <div className="mt-2 space-y-1.5">
                      {contact.options.map((option, optIdx) => (
                        <div key={optIdx} className="flex items-start gap-2 text-xs text-blue-700 pl-2 border-l-2 border-blue-300">
                          <svg className="w-3 h-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                          </svg>
                          <span>
                            {option.number && <span className="font-semibold">Option {option.number}: </span>}
                            {option.description}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                // Simple contact display (backward compatibility)
                <div className="text-sm text-blue-800">
                  <p className="font-mono font-medium">{contact}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EmergencyContacts;
