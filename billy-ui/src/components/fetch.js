import AuthService from '../services/auth-service'
const { fetch: originalFetch } = window;

// window.fetch = async (...args) => {
//   let [resource, config] = args;
//   let response = await originalFetch(resource, config);
//   if (!response.ok && [401, 403].includes(response.status)) {
//     console.log('Authentication error.')
//     AuthService.logout()
//   }
//   return response;
// };

export default window.fetch;