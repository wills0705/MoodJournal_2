import axios from 'axios';

// create axios
const instance = axios.create({
  baseURL: 'https://api.example.com', // set api
  timeout: 10000, // request limit time
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，比如设置 token
    // config.headers['Authorization'] = 'Bearer your-token';
    return config;
  },
  error => {
    // 处理请求错误
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response;
  },
  error => {
    // 处理响应错误
    return Promise.reject(error);
  }
);

// 封装请求方法
const request = {
  get(url, params = {}) {
    return instance.get(url, { params });
  },
  post(url, data = {}) {
    return instance.post(url, data);
  },
  put(url, data = {}) {
    return instance.put(url, data);
  },
  delete(url, params = {}) {
    return instance.delete(url, { params });
  },
};

export default request;