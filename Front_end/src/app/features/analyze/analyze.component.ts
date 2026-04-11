import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { JobFitService } from '../../services/job-fit.service';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TextareaModule } from 'primeng/textarea';
import { MessageModule } from 'primeng/message';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-analyze',
  standalone: true,
  imports: [
    FormsModule,
    ButtonModule,
    InputTextModule,
    TextareaModule,
    MessageModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './analyze.component.html',
  styleUrl: './analyze.component.scss',
})
export class AnalyzeComponent {
  private router = inject(Router);
  private jobFitService = inject(JobFitService);
  private messageService = inject(MessageService);

  selectedFiles: File[] = [];
  jobTitle = '';
  jobDescription = '';
  isScreening = false;

  get fileCount(): number {
    return this.selectedFiles.length;
  }

  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;

    const validFiles: File[] = [];
    const rejected: string[] = [];

    Array.from(input.files).forEach((file) => {
      if (file.name.toLowerCase().endsWith('.pdf')) {
        validFiles.push(file);
      } else {
        rejected.push(file.name);
      }
    });

    this.selectedFiles = validFiles;

    if (rejected.length > 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Unsupported files skipped',
        detail: `Only PDF files are accepted. Skipped: ${rejected.join(', ')}`,
      });
    }
  }

  removeFile(index: number): void {
    this.selectedFiles = this.selectedFiles.filter((_, i) => i !== index);
  }

  onSubmit(): void {
    if (this.selectedFiles.length === 0) {
      this.messageService.add({
        severity: 'warn',
        summary: 'No files selected',
        detail: 'Please upload at least one PDF resume.',
      });
      return;
    }

    if (!this.jobDescription.trim()) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Job description required',
        detail: 'Please paste the job description before screening.',
      });
      return;
    }

    if (this.jobDescription.trim().length < 30) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Description too short',
        detail: 'Job description must be at least 30 characters.',
      });
      return;
    }

    this.isScreening = true;

    this.jobFitService.screen(this.selectedFiles, this.jobDescription.trim()).subscribe({
      next: (result) => {
        this.isScreening = false;
        this.router.navigate(['/results'], {
          state: {
            result,
            jobTitle: this.jobTitle.trim() || 'Screening Results',
          },
        });
      },
      error: (err) => {
        this.isScreening = false;
        const detail =
          err?.error?.detail ?? 'Something went wrong while calling the API.';
        this.messageService.add({
          severity: 'error',
          summary: 'Screening failed',
          detail,
        });
      },
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}
