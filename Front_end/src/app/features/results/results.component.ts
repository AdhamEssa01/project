import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { ScreeningResponse, CandidateResult } from '../../services/job-fit.service';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { ButtonModule } from 'primeng/button';
import { MessageModule } from 'primeng/message';
import { TooltipModule } from 'primeng/tooltip';
import { ProgressBarModule } from 'primeng/progressbar';
import { DecimalPipe, NgClass } from '@angular/common';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [
    TableModule,
    TagModule,
    ButtonModule,
    MessageModule,
    TooltipModule,
    ProgressBarModule,
    DecimalPipe,
    NgClass,
  ],
  templateUrl: './results.component.html',
  styleUrl: './results.component.scss',
})
export class ResultsComponent implements OnInit {
  private router = inject(Router);

  result: ScreeningResponse | null = null;
  jobTitle = 'Screening Results';

  ngOnInit(): void {
    const state = history.state as { result?: ScreeningResponse; jobTitle?: string };

    if (!state?.result) {
      // Guard: navigated here directly without data
      this.router.navigate(['/analyze']);
      return;
    }

    this.result = state.result;
    this.jobTitle = state.jobTitle || 'Screening Results';
  }

  /** PrimeNG Tag severity based on label */
  labelSeverity(label: string): 'success' | 'warn' | 'danger' | 'secondary' {
    if (label === 'Good Fit') return 'success';
    if (label === 'Potential Fit') return 'warn';
    if (label === 'No Fit') return 'danger';
    return 'secondary';
  }

  /** Score as integer percent for the progress bar */
  scorePercent(score: number): number {
    return Math.round(score * 100);
  }

  screenAgain(): void {
    this.router.navigate(['/analyze']);
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}
