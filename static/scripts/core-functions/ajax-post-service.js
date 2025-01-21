// responsible for sending all the ajax post requests to the server

export default class AjaxPostService {
    static async post(url, data, {token = null, header = {}, queryParams= {}, timeout = 0} = {}) {
        try {
            if (Object.keys(queryParams).length) {
                const queryString = new URLSearchParams(queryParams).toString();
                url = `${url}?${queryString}`;
            }

            // Add auth header if token
            if (token) {
                header['Authorization'] = `Bearer ${token}`;
            }

            // Set the timeout
            const controller = new AbortController();
            const signal = controller.signal;
            if (timeout) {
                setTimeout(() => controller.abort(), timeout);
            }

            // perform the fetch

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...header
                },
                body: JSON.stringify(data),
                signal
            });

            // check if the response is ok
            if (!response.ok) {
                throw new Error(response.statusText);
            }

            // return the response
            return await response.json();
    } catch (error) { // catch any errors
        console.error(error);
        throw new Error(error);
    }
    }
}
