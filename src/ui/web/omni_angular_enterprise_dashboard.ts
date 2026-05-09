// OMNI UI Layer
// Angular Enterprise Dashboard
// Based on angular/angular. Provides an RxJS-powered frontend for Omni.

import { Component, OnInit, OnDestroy } from '@angular/core';
import { Observable, Subscription, interval } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';

interface OmniSystemState {
    version: string;
    memoryUsageMb: number;
    tasksProcessed: number;
}

@Component({
    selector: 'omni-enterprise-dashboard',
    template: `
        <div class="omni-ng-dashboard">
            <h2>OMNI Control Center (Angular)</h2>
            <div *ngIf="error" class="error-banner">
                Connection to Universal Engine lost. Retrying...
            </div>
            <div class="metrics-panel" *ngIf="state">
                <div class="metric">
                    <label>Engine Version</label>
                    <span>{{ state.version }}</span>
                </div>
                <div class="metric">
                    <label>Memory Usage</label>
                    <span>{{ state.memoryUsageMb | number:'1.2-2' }} MB</span>
                </div>
                <div class="metric">
                    <label>Tasks Processed</label>
                    <span>{{ state.tasksProcessed | number }}</span>
                </div>
            </div>
        </div>
    `,
    styles: [`
        .omni-ng-dashboard { padding: 20px; font-family: 'Inter', sans-serif; }
        .metrics-panel { display: flex; gap: 20px; margin-top: 20px; }
        .metric { background: #f5f5f5; padding: 15px; border-radius: 8px; min-width: 150px; }
        .metric label { display: block; font-size: 12px; color: #666; text-transform: uppercase; }
        .metric span { font-size: 24px; font-weight: bold; color: #333; }
        .error-banner { background: #fee; color: #c00; padding: 10px; border-radius: 4px; }
    `]
})
export class OmniAngularDashboardComponent implements OnInit, OnDestroy {
    public state: OmniSystemState | null = null;
    public error: boolean = false;
    private pollingSub: Subscription | null = null;

    constructor(private http: HttpClient) {
        console.log("OMNI Angular: Dashboard Component Initialized.");
    }

    ngOnInit() {
        // Poll the Omni REST Gateway every 2 seconds
        this.pollingSub = interval(2000).pipe(
            switchMap(() => this.http.get<OmniSystemState>('/api/v1/omni/state').pipe(
                catchError(err => {
                    console.error("OMNI Angular Error:", err);
                    this.error = true;
                    throw err; // Re-throw to keep observable chain active if handled by a retry
                })
            ))
        ).subscribe(
            data => {
                this.state = data;
                this.error = false;
            },
            err => {
                // Keep previous state, show error flag
                this.error = true;
            }
        );
    }

    ngOnDestroy() {
        if (this.pollingSub) {
            this.pollingSub.unsubscribe();
        }
    }
}
