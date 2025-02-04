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

  private getHeaders(customHeaders?: object): HttpHeaders {
    let headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    const token = localStorage.getItem('authToken');
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
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
    customHeaders?: object
  ): Observable<T> {
    return this.http
      .request<T>(method, `${this.apiUrl}/${endpoint}`, {
        body,
        headers: this.getHeaders(customHeaders),
      })
      .pipe(catchError(this.handleError));
  }

  get<T>(endpoint: string, customHeaders?: object): Observable<T> {
    return this.request<T>('GET', endpoint, null, customHeaders);
  }

  post<T>(endpoint: string, data: any, customHeaders?: object): Observable<T> {
    return this.request<T>('POST', endpoint, data, customHeaders);
  }

  put<T>(endpoint: string, data: any, customHeaders?: object): Observable<T> {
    return this.request<T>('PUT', endpoint, data, customHeaders);
  }

  delete<T>(endpoint: string, customHeaders?: object): Observable<T> {
    return this.request<T>('DELETE', endpoint, null, customHeaders);
  }

  private handleError(error: any) {
    console.error('API request error:', error);
    console.error(error.error.message)
    return throwError(() => new Error(error.error.message || 'Server error'));
  }
}
