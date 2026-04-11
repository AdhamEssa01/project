import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// ── Single-candidate response ─────────────────────────────────────────────────

export interface SingleFitResponse {
  label: string;
  score: number;
}

// ── Batch screening response ──────────────────────────────────────────────────

export interface CandidateResult {
  filename: string;
  rank: number;
  label: string;    // Good Fit | Potential Fit | No Fit
  score: number;
  status: string;   // shortlisted | review | rejected
}

export interface FileError {
  filename: string;
  error: string;
}

export interface ScreeningSummary {
  total_candidates: number;
  good_fit_count: number;
  potential_fit_count: number;
  no_fit_count: number;
  good_fit_pct: number;
  potential_fit_pct: number;
  no_fit_pct: number;
  top_candidates: string[];
}

export interface ScreeningResponse {
  job_description_preview: string;
  summary: ScreeningSummary;
  candidates: CandidateResult[];
  errors: FileError[];
}

// ── Service ───────────────────────────────────────────────────────────────────

@Injectable({ providedIn: 'root' })
export class JobFitService {
  private http = inject(HttpClient);
  private apiBase = environment.apiBase;

  /** Single CV screening — keeps backward compatibility. */
  analyze(file: File, jobDescription: string): Observable<SingleFitResponse> {
    const formData = new FormData();
    formData.append('resume_text_pdf', file);
    formData.append('job_description_text', jobDescription);
    return this.http.post<SingleFitResponse>(`${this.apiBase}/job-fit`, formData);
  }

  /** Batch recruiter screening — sends multiple PDFs against one job description. */
  screen(files: File[], jobDescription: string): Observable<ScreeningResponse> {
    const formData = new FormData();
    files.forEach((file) => formData.append('resumes', file));
    formData.append('job_description_text', jobDescription);
    return this.http.post<ScreeningResponse>(`${this.apiBase}/screen`, formData);
  }
}
