import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { from, Observable, throwError } from 'rxjs';
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

  downloadFile(fileName: string): void {
    this.http
      .get(`${this.apiUrl}/download/${fileName}`, {
        headers: this.getHeaders(),
        responseType: 'blob',
      })
      .pipe(catchError(this.handleError))
      .subscribe((blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
  }

  getStream(endpoint: string, customHeaders?: object): Observable<string> {
    return new Observable<string>((observer) => {
      const token = localStorage.getItem('authToken');

      const headers: Record<string, string> = {
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(customHeaders as Record<string, string> ?? {}),
      };

      const controller = new AbortController(); // Support cancellation
      const request = fetch(`${this.apiUrl}/${endpoint}`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });

      from(request)
        .pipe(
          catchError((error) => {
            observer.error(error);
            return throwError(() => new Error('Failed to fetch stream.'));
          })
        )
        .subscribe((response) => {
          if (!response.ok || !response.body) {
            observer.error(new Error(`HTTP error! Status: ${response.status}`));
            return;
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();

          const readStream = async () => {
            try {
              while (true) {
                const { done, value } = await reader.read();
                if (done) {
                  observer.complete();
                  break;
                }
                const chunk = decoder.decode(value, { stream: true });
                observer.next(chunk);
              }
            } catch (error) {
              observer.error(error);
            }
          };

          readStream();
        });

      return () => {
        controller.abort();
      };
    });
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
