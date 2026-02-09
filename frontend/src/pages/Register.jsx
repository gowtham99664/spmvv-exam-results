import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { validateEmail, validatePassword, sanitizeInput } from '../utils/validation';

const Register = () => {
  const [formData, setFormData] = useState({
    rollNumber: '',
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: sanitizeInput(value) }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.rollNumber.trim()) {
      newErrors.rollNumber = 'Roll Number is required';
    } else if (formData.rollNumber.length < 3) {
      newErrors.rollNumber = 'Roll Number must be at least 3 characters';
    }
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First Name is required';
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last Name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.message;
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    try {
      const userData = {
        roll_number: formData.rollNumber,
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword
      };
      const result = await register(userData);
      if (result.success) {
        alert('Registration successful!');
        navigate('/login');
      } else {
        setErrors({ general: result.error });
      }
    } catch (error) {
      setErrors({ general: 'An error occurred.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-800 mb-2">Student Registration</h1>
          <p className="text-gray-600">Create your account</p>
        </div>
        <div className="bg-white rounded-lg shadow-xl p-8">
          <form onSubmit={handleSubmit}>
            {errors.general && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">{errors.general}</div>}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Roll Number *</label>
              <input type="text" name="rollNumber" value={formData.rollNumber} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.hallTicketNumber && <p className="error-message">{errors.rollNumber}</p>}
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
              <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.name && <p className="error-message">{errors.firstName}</p>}
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.email && <p className="error-message">{errors.email}</p>}
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number *</label>
              <input type="tel" name="lastName" value={formData.lastName} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.phone && <p className="error-message">{errors.lastName}</p>}
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Password *</label>
              <input type="password" name="password" value={formData.password} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.password && <p className="error-message">{errors.password}</p>}
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password *</label>
              <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} className="input-field" disabled={loading} />
              {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">{loading ? 'Registering...' : 'Register'}</button>
          </form>
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">Already have an account? <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">Login here</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
