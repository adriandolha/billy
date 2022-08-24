import AuthService from '../services/auth-service'
const { fetch: originalFetch } = window;

window.fetch = async (...args) => {
  let [resource, config] = args;
  let response = await originalFetch(resource, config);
  if (!response.ok && response.status === 401) {
    console.log('Authentication error.')
    AuthService.getCurrentUser() && AuthService.logout()
  }
  return response;
};

export default fetch;