import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'omni-cluster-view',
  template: `
    <div class="omni-card">
      <h2>OMNI Cluster Nodes</h2>
      <ul>
        <li *ngFor="let node of nodes" [class.healthy]="node.status === 'OK'">
          {{ node.id }} - {{ node.role }} (Load: {{ node.load }}%)
        </li>
      </ul>
      <button (click)="refreshNodes()">Refresh</button>
    </div>
  `,
  styles: [`
    .omni-card { background: #222; color: white; padding: 20px; border-radius: 8px; }
    .healthy { color: #0f0; }
    button { background: #007bff; color: white; border: none; padding: 10px; cursor: pointer; }
  `]
})
export class OmniClusterViewComponent implements OnInit {
  nodes = [
    { id: 'node-alpha', role: 'Inference', status: 'OK', load: 45 },
    { id: 'node-beta', role: 'Storage', status: 'OK', load: 12 }
  ];

  ngOnInit() {
    console.log("OMNI Angular Cluster View Initialized.");
  }

  refreshNodes() {
    this.nodes.forEach(n => n.load = Math.floor(Math.random() * 100));
  }
}
