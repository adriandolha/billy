const API_URL = "http://localhost:8000/api/auth/";

class AuthService {
  logout() {
    localStorage.removeItem("user");
    window.location.reload(true);
    window.location.href="/home"
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));;
  }
}

export default new AuthService();
