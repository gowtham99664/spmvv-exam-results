import DOMPurify from 'dompurify';

// Sanitize input to prevent XSS
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] });
};

// Email validation
export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
};

// Password validation (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
export const validatePassword = (password) => {
  if (password.length < 8) {
    return { valid: false, message: 'Password must be at least 8 characters long' };
  }
  if (!/[A-Z]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one uppercase letter' };
  }
  if (!/[a-z]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one lowercase letter' };
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'Password must contain at least one number' };
  }
  return { valid: true, message: '' };
};

// Hall ticket validation (alphanumeric, 6-20 chars)
export const validateHallTicket = (hallTicket) => {
  const re = /^[A-Z0-9]{6,20}$/;
  return re.test(hallTicket);
};

// File validation for Excel uploads
export const validateExcelFile = (file) => {
  const maxSize = 5 * 1024 * 1024; // 5MB
  const allowedTypes = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv'
  ];
  
  if (!file) {
    return { valid: false, message: 'Please select a file' };
  }
  
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, message: 'Please upload a valid Excel or CSV file (.xlsx, .xls, .csv)' };
  }
  
  if (file.size > maxSize) {
    return { valid: false, message: 'File size must be less than 5MB' };
  }
  
  return { valid: true, message: '' };
};

// Form data sanitization
export const sanitizeFormData = (formData) => {
  const sanitized = {};
  for (const [key, value] of Object.entries(formData)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else {
      sanitized[key] = value;
    }
  }
  return sanitized;
};
