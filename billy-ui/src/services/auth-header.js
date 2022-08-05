export default function authHeader() {
    const user = JSON.parse(localStorage.getItem('user'));
    // console.log(user)
    if (user && user.id_token) {
      return { Authorization: user.id_token };
    } else {
      return {};
    }
  }