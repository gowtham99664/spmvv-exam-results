# SPMVV Exam Results Management System - Frontend

React.js frontend application for the SPMVV Exam Results Management System.

## Features

- **Student Portal**
  - Student registration and login
  - View exam results by semester
  - Real-time notifications
  - Change password functionality

- **Admin Portal**
  - Admin login
  - Upload exam results via Excel files
  - View all results with search functionality
  - Change password functionality

- **Security Features**
  - JWT token-based authentication
  - CSRF token protection
  - XSS protection with input sanitization
  - Secure session management
  - Protected routes based on user roles

## Tech Stack

- React 18
- React Router v6
- Axios for API calls
- Tailwind CSS for responsive design
- Vite for fast development and building
- DOMPurify for XSS protection
- React Icons for UI icons

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
Copy `.env.example` to `.env` and update the API URL:
```
VITE_API_URL=http://your-backend-url:5000/api
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
frontend/
├── public/            # Static assets
├── src/
│   ├── components/    # Reusable React components
│   │   ├── Navbar.jsx
│   │   ├── NotificationBell.jsx
│   │   ├── ProtectedRoute.jsx
│   │   └── ChangePasswordModal.jsx
│   ├── context/       # React Context for state management
│   │   └── AuthContext.jsx
│   ├── pages/         # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── StudentDashboard.jsx
│   │   └── AdminDashboard.jsx
│   ├── services/      # API service layer
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── resultsService.js
│   │   └── notificationService.js
│   ├── utils/         # Utility functions
│   │   ├── validation.js
│   │   └── tokenManager.js
│   ├── App.jsx        # Main app component
│   ├── main.jsx       # Entry point
│   └── index.css      # Global styles
├── .env               # Environment variables
├── .env.example       # Environment variables template
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
└── tailwind.config.js # Tailwind CSS configuration
```

## API Integration

The frontend communicates with the backend API using Axios with interceptors for:
- Adding JWT tokens to requests
- Handling token refresh automatically
- CSRF token management
- Error handling and session expiration

## Security Measures

1. **Input Sanitization**: All user inputs are sanitized using DOMPurify to prevent XSS attacks
2. **Token Management**: JWT tokens stored in sessionStorage (more secure than localStorage)
3. **Protected Routes**: Role-based access control for admin and student routes
4. **CSRF Protection**: CSRF tokens included in API requests
5. **Content Security Policy**: CSP headers configured in index.html

## Available Scripts

- `npm run dev` - Start development server on port 3000
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Responsive Design

The application is fully responsive and works on:
- Desktop (1024px and above)
- Tablet (768px - 1023px)
- Mobile (below 768px)

## License

Proprietary - SPMVV University
