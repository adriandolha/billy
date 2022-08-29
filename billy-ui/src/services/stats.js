import authHeader from "./auth-header";
import { API_URL } from "../pages/config";
// import fetch from "../components/fetch"

class StatsService {
    expenses_per_month() {
        return fetch(`${API_URL}/billy/stats/expenses_per_month`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    expenses_per_month_and_category() {
        return fetch(`${API_URL}/billy/stats/expenses_per_month_and_category`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    avg_expenses_per_category() {
        return fetch(`${API_URL}/billy/stats/avg_expenses_per_category`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
}

export default new StatsService();
