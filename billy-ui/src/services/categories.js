import authHeader from "./auth-header";
import { API_URL } from "../pages/config";
// import fetch from "../components/fetch"

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
    save_category(category) {
        return fetch(`${API_URL}/billy/categories/${category.name}`, {
            method: 'put',
            headers: new Headers({
                ...authHeader(),
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify(category)
        })
    }

}

export default new CategoryService();
