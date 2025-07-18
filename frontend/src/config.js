// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://davidpascual13.pythonanywhere.com'  // Your PythonAnywhere API URL
  : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:5000'
  : 'https://didactic-space-robot-jjrjxxp79rqrhpv7g-5000.app.github.dev';

export { API_BASE_URL };
