import authHeader from "./auth-header";
import { API_URL } from "../pages/config";
// import fetch from "../components/fetch"

class BankStatementService {
    search(query, limit, offset) {
        console.log(API_URL)
        return fetch(`${API_URL}/billy/bank_statements/search?query=${query}&limit=${limit}&offset=${offset}`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
}

export default new BankStatementService();
