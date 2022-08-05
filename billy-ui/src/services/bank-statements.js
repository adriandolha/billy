import authHeader from "./auth-header";
import { API_URL } from "../pages/config";

class BankStatementService {
    search(query, limit, offset) {
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
