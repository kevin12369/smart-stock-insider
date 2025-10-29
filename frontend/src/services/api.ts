/**
 * API 客户端
 *
 * 提供统一的API调用接口，包含请求拦截、响应处理、错误处理等功能
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from 'antd';

// API响应类型
export interface ApiResponse<T = any> {
  data: T;
  code: number;
  message: string;
  timestamp: string;
}

// 错误响应类型
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
  path: string;
}

class ApiClient {
  private instance: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api';
    this.instance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * 设置请求和响应拦截器
   */
  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加时间戳防止缓存
        if (config.method === 'get') {
          config.params = {
            ...config.params,
            _t: Date.now(),
          };
        }

        // 添加请求日志
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);

        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // 添加响应日志
        console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);

        return response;
      },
      (error) => {
        console.error('❌ Response Error:', error);

        // 统一错误处理
        this.handleError(error);

        return Promise.reject(error);
      }
    );
  }

  /**
   * 错误处理
   */
  private handleError(error: any) {
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;
      const errorData = data as ErrorResponse;

      switch (status) {
        case 400:
          message.error('请求参数错误');
          break;
        case 401:
          message.error('未授权访问');
          break;
        case 403:
          message.error('权限不足');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 429:
          message.error('请求过于频繁，请稍后再试');
          break;
        case 500:
          message.error('服务器内部错误');
          break;
        case 502:
          message.error('网关错误');
          break;
        case 503:
          message.error('服务暂时不可用');
          break;
        default:
          message.error(errorData?.error?.message || '请求失败');
      }

      console.error('API Error:', {
        status,
        data: errorData,
        url: error.config?.url,
      });
    } else if (error.request) {
      // 请求已发出但没有收到响应
      if (error.code === 'ECONNABORTED') {
        message.error('请求超时，请检查网络连接');
      } else {
        message.error('网络连接失败，请检查网络设置');
      }
    } else {
      // 其他错误
      message.error('请求配置错误');
    }
  }

  /**
   * GET 请求
   */
  async get<T = any>(
    url: string,
    params?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    return this.instance.get(url, { params, ...config });
  }

  /**
   * POST 请求
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    return this.instance.post(url, data, config);
  }

  /**
   * PUT 请求
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    return this.instance.put(url, data, config);
  }

  /**
   * PATCH 请求
   */
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    return this.instance.patch(url, data, config);
  }

  /**
   * DELETE 请求
   */
  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    return this.instance.delete(url, config);
  }

  /**
   * 上传文件
   */
  async upload<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  }

  /**
   * 下载文件
   */
  async download(
    url: string,
    filename?: string,
    config?: AxiosRequestConfig
  ): Promise<void> {
    try {
      const response = await this.instance.get(url, {
        ...config,
        responseType: 'blob',
      });

      // 创建下载链接
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download failed:', error);
      throw error;
    }
  }

  /**
   * 设置请求头
   */
  setHeader(key: string, value: string): void {
    this.instance.defaults.headers.common[key] = value;
  }

  /**
   * 移除请求头
   */
  removeHeader(key: string): void {
    delete this.instance.defaults.headers.common[key];
  }

  /**
   * 设置认证token
   */
  setAuthToken(token: string): void {
    this.setHeader('Authorization', `Bearer ${token}`);
  }

  /**
   * 移除认证token
   */
  removeAuthToken(): void {
    this.removeHeader('Authorization');
  }

  /**
   * 取消请求
   */
  createCancelToken() {
    return axios.CancelToken.source();
  }

  /**
   * 检查是否为取消错误
   */
  isCancel(error: any): boolean {
    return axios.isCancel(error);
  }
}

// 创建全局API客户端实例
export const apiClient = new ApiClient();

// 导出默认实例
export default apiClient;

// 导出便捷方法
export const api = {
  get: <T = any>(url: string, params?: any, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, params, config),
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config),
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config),
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config),
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config),
};