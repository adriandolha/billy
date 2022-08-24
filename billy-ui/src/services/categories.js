import authHeader from "./auth-header";
import { API_URL } from "../pages/config";
import fetch from "../components/fetch"

class CategoryService {
    get_all() {
        console.log(API_URL)
        return fetch(`${API_URL}/billy/categories`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
}

export default new CategoryService();
