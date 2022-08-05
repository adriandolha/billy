const API_URL = "http://localhost:8000/api/auth/";

class AuthService {
  logout() {
    localStorage.removeItem("user");
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));;
  }
}

export default new AuthService();
