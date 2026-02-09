# SPMVV Exam Results Frontend - Installation Guide

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager

## Quick Start

### 1. Navigate to the frontend directory
```bash
cd ~/spmvv-exam-results/frontend
```

### 2. Install Dependencies
```bash
npm install
```

This will install all required packages:
- React 18
- React Router DOM v6
- Axios
- Tailwind CSS
- Vite
- DOMPurify
- React Icons

### 3. Configure Environment Variables

The .env file has already been created with:
```
VITE_API_URL=http://10.127.248.83:5000/api
VITE_APP_NAME=SPMVV Exam Results
VITE_MAX_FILE_SIZE=5242880
```

If you need to change the backend API URL, edit the `.env` file.

### 4. Start Development Server
```bash
npm run dev
```

The application will be available at: http://10.127.248.83:3000

### 5. Build for Production
```bash
npm run build
```

The production build will be created in the `dist` directory.

### 6. Preview Production Build
```bash
npm run preview
```

## Deployment

### Option 1: Serve with Nginx

1. Build the production version:
```bash
npm run build
```

2. Copy the `dist` directory contents to your web server:
```bash
sudo cp -r dist/* /var/www/html/spmvv-results/
```

3. Configure Nginx (example):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html/spmvv-results;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: Run with PM2

1. Install PM2:
```bash
npm install -g pm2
```

2. Create a serve script:
```bash
npm install -g serve
pm2 start "serve -s dist -l 3000" --name spmvv-frontend
pm2 save
pm2 startup
```

## File Structure Summary

```
frontend/
├── public/                     # Static assets
│   └── vite.svg
├── src/
│   ├── components/             # Reusable components
│   │   ├── ChangePasswordModal.jsx
│   │   ├── Navbar.jsx
│   │   ├── NotificationBell.jsx
│   │   └── ProtectedRoute.jsx
│   ├── context/                # React Context
│   │   └── AuthContext.jsx
│   ├── pages/                  # Page components
│   │   ├── AdminDashboard.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── StudentDashboard.jsx
│   ├── services/               # API services
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── notificationService.js
│   │   └── resultsService.js
│   ├── utils/                  # Utility functions
│   │   ├── tokenManager.js
│   │   └── validation.js
│   ├── App.jsx                 # Main app
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── .env                        # Environment variables
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── index.html                  # HTML template
├── package.json                # Dependencies
├── postcss.config.js           # PostCSS config
├── tailwind.config.js          # Tailwind config
├── vite.config.js              # Vite config
├── README.md                   # Documentation
└── INSTALLATION.md             # This file

Total Files Created: 27
```

## Features Implemented

### Authentication & Authorization
✓ JWT token-based authentication
✓ Role-based access control (Admin/Student)
✓ Protected routes
✓ Automatic token refresh
✓ Session expiration handling

### Security
✓ XSS protection with DOMPurify
✓ CSRF token handling
✓ Secure token storage (sessionStorage)
✓ Input validation and sanitization
✓ Content Security Policy headers

### Student Features
✓ Student registration
✓ Student login
✓ View results by semester
✓ Notification system with unread count
✓ Change password functionality

### Admin Features
✓ Admin login
✓ Upload Excel files with validation
✓ View all results
✓ Search results by hall ticket
✓ Change password functionality

### UI/UX
✓ Responsive design (mobile/tablet/desktop)
✓ Loading states and error handling
✓ Form validation with user feedback
✓ Modern Tailwind CSS styling
✓ Icon integration with React Icons

## Troubleshooting

### Port Already in Use
If port 3000 is already in use, modify `vite.config.js`:
```javascript
export default defineConfig({
  server: {
    port: 3001,  // Change to any available port
  }
})
```

### CORS Issues
Ensure your backend API has CORS configured to allow requests from:
- http://10.127.248.83:3000 (development)
- Your production domain

### API Connection Failed
1. Check if backend is running: `curl http://10.127.248.83:5000/api/health`
2. Verify `.env` file has correct API URL
3. Check network connectivity

## Next Steps

1. Install dependencies: `npm install`
2. Start development server: `npm run dev`
3. Test the application with your backend
4. Build for production when ready: `npm run build`

## Support

For issues or questions, contact the development team.
