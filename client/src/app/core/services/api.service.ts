import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../environment/environment';

@Injectable({
  providedIn: 'root',
})

export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  private getHeaders(customHeaders?: object, isFileUpload: boolean = false): HttpHeaders {
    let headers = new HttpHeaders();

    const token = localStorage.getItem('authToken');
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }

    if (!isFileUpload) {
      headers = headers.set('Content-Type', 'application/json');
    }

    if (customHeaders) {
      Object.entries(customHeaders).forEach(([key, value]) => {
        headers = headers.set(key, value as string);
      });
    }

    return headers;
  }

  request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    body?: any,
    customHeaders?: object,
    isFileUpload: boolean = false
  ): Observable<T> {
    return this.http
      .request<T>(method, `${this.apiUrl}/${endpoint}`, {
        body,
        headers: this.getHeaders(customHeaders, isFileUpload),
      })
      .pipe(catchError(this.handleError));
  }

  get<T>(endpoint: string, customHeaders?: object): Observable<T> {
    return this.request<T>('GET', endpoint, null, customHeaders);
  }

  post<T>(endpoint: string, data: any, customHeaders?: object, isFileUpload: boolean = false): Observable<T> {
    return this.request<T>('POST', endpoint, data, customHeaders, isFileUpload);
  }

  put<T>(endpoint: string, data: any, customHeaders?: object): Observable<T> {
    return this.request<T>('PUT', endpoint, data, customHeaders);
  }

  delete<T>(endpoint: string, customHeaders?: object): Observable<T> {
    return this.request<T>('DELETE', endpoint, null, customHeaders);
  }

  private handleError(error: any) {
    console.error('API request error:', error);
    
    const errorMessage = error?.error?.message || 'Server error';
    const errorStatus = error?.status || 500;

    return throwError(() => ({
      message: errorMessage,
      status: errorStatus,
    }));
  }
}
