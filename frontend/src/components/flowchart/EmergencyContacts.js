import React from 'react';

const EmergencyContacts = ({ contacts }) => {
  if (!contacts || Object.keys(contacts).length === 0) {
    return null;
  }

  return (
    <div className="mt-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-xl p-8 shadow-xl">
      <h3 className="font-bold text-blue-900 mb-6 text-2xl flex items-center gap-3">
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
        Emergency Contacts Quick Reference
      </h3>
      <div className="grid grid-cols-3 gap-6">
        {Object.entries(contacts).map(([name, contact], idx) => (
          <div key={idx} className="bg-white/70 rounded-lg p-5 border border-blue-200 hover:shadow-md transition-shadow">
            <h4 className="font-semibold text-blue-900 mb-3">{name}</h4>
            <div className="text-sm text-blue-800">
              <p className="font-mono font-medium">{contact}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmergencyContacts;
