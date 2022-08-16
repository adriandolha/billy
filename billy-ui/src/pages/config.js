const DRAWER_WIDTH = 240
const local = {
    API_URL: 'http://localhost:3000'
}
const dev = {
    API_URL: 'https://vjmeqvvnq9.execute-api.eu-central-1.amazonaws.com/Dev'
}
const prod = {
    API_URL: 'https://yq751grmbg.execute-api.eu-central-1.amazonaws.com/Dev'
}
const env = () => {
    const host = window.location.host
    if (host.startsWith('localhost')) {
        return local;
    }
    if (host.startsWith('www.dev')) {
        return dev;
    }
    if (host.startsWith('www.billy')) {
        return prod;
    }
}

const API_URL = env().API_URL;

export { DRAWER_WIDTH, API_URL };
