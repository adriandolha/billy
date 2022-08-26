import authHeader from "./auth-header";
import { API_URL } from "../pages/config";
// import fetch from "../components/fetch"

class JobService {
    get_all() {
        console.log(API_URL)
        return fetch(`${API_URL}/billy/jobs`, {
            method: 'get',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
    delete_job(job_id) {
        console.log(API_URL)
        return fetch(`${API_URL}/billy/jobs/${job_id}`, {
            method: 'delete',
            headers: new Headers({
                'Content-Type': 'application/json',
                ...authHeader()
            })
        })
    }
}

export default new JobService();
