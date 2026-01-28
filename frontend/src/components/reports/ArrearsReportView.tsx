import { Badge } from '../Badge';
import { Card } from '../Card';

interface LedgerData {
  tenancy_id: string;
  tenant: {
    name: string;
    email: string;
    phone: string;
    lease_start: string;
    lease_end: string;
  };
  property: {
    address: string;
    weekly_rent: number;
    bond_held: number;
  };
  financial_summary: {
    current_balance: number;
    rent_paid_to_date: string;
    days_in_arrears: number;
    last_payment: {
      amount: number;
      date: string;
      method: string;
    };
  };
  payment_history: {
    last_12_months: {
      on_time: number;
      late_1_7_days: number;
      late_8_14_days: number;
      late_14_plus_days: number;
    };
    payment_reliability_score: number;
  };
  arrears_history: { date: string; amount: number; note: string }[];
}

interface BreachData {
  tenancy_id: string;
  assessment_date: string;
  arrears_status: {
    is_in_arrears: boolean;
    days_overdue: number;
    amount_overdue: number;
    breach_threshold_days: number;
    breach_threshold_met: boolean;
  };
  breach_risk: {
    level: string;
    score: number;
    factors: { factor: string; impact: string; value: string }[];
  };
  regulatory_context: {
    state: string;
    notice_type: string;
    minimum_notice_period: string;
    can_issue_notice: boolean;
  };
  recommended_action: string;
  communication_history: { date: string; type: string; message: string }[];
}

interface RiskClassificationData {
  classification_timestamp: string;
  risk_assessment: {
    overall_level: string;
    confidence_score: number;
    requires_immediate_action: boolean;
  };
  recommended_workflow: {
    immediate: { step: number; action: string; assignee: string; deadline: string }[];
    follow_up: { action: string; timeline: string }[];
  };
  compliance_checklist: { item: string; status: string }[];
  breach_notice_preview: {
    notice_type: string;
    form_number: string;
    termination_date: string;
    amount_to_remedy: string;
  };
}

interface ArrearsReportViewProps {
  ledgerData: LedgerData;
  breachData: BreachData;
  riskData: RiskClassificationData;
}

export function ArrearsReportView({ ledgerData, breachData, riskData }: ArrearsReportViewProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-AU', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD' }).format(Math.abs(amount));
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-danger';
      case 'high': return 'text-danger';
      case 'medium': return 'text-warning';
      case 'low': return 'text-success';
      default: return 'text-text-secondary';
    }
  };

  const getRiskBgColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'bg-danger/10 border-danger/30';
      case 'high': return 'bg-danger/10 border-danger/30';
      case 'medium': return 'bg-warning/10 border-warning/30';
      case 'low': return 'bg-success/10 border-success/30';
      default: return 'bg-bg-tertiary border-border-subtle';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Risk Alert */}
      <div className={`p-6 rounded-xl border-2 ${getRiskBgColor(breachData.breach_risk.level)}`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-text-primary">Arrears Assessment</h2>
              <Badge 
                variant={breachData.breach_risk.level === 'high' ? 'error' : breachData.breach_risk.level === 'medium' ? 'warning' : 'success'}
                size="md"
              >
                {breachData.breach_risk.level.toUpperCase()} RISK
              </Badge>
            </div>
            <p className="text-text-secondary">{ledgerData.property.address}</p>
            <p className="text-sm text-text-muted mt-1">
              Tenancy: {ledgerData.tenancy_id} • Assessment: {formatDate(breachData.assessment_date)}
            </p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getRiskColor(breachData.breach_risk.level)}`}>
              {formatCurrency(breachData.arrears_status.amount_overdue)}
            </div>
            <p className="text-sm text-text-muted">{breachData.arrears_status.days_overdue} days overdue</p>
          </div>
        </div>
      </div>

      {/* Risk Score Gauge */}
      <Card variant="default">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Risk Assessment Score
        </h3>
        <div className="flex items-center gap-8">
          {/* Score Circle */}
          <div className="relative w-32 h-32">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="56" fill="none" stroke="currentColor" className="text-bg-secondary" strokeWidth="12" />
              <circle 
                cx="64" cy="64" r="56" fill="none" 
                stroke="currentColor" 
                className={getRiskColor(breachData.breach_risk.level)}
                strokeWidth="12"
                strokeDasharray={`${(breachData.breach_risk.score / 100) * 352} 352`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-3xl font-bold ${getRiskColor(breachData.breach_risk.level)}`}>
                {breachData.breach_risk.score}
              </span>
            </div>
          </div>

          {/* Factors */}
          <div className="flex-1 space-y-3">
            {breachData.breach_risk.factors.map((factor, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
                <div>
                  <div className="font-medium text-text-primary">{factor.factor}</div>
                  <div className="text-sm text-text-muted">{factor.value}</div>
                </div>
                <Badge 
                  variant={factor.impact === 'high' ? 'error' : factor.impact === 'medium' ? 'warning' : 'info'} 
                  size="sm"
                >
                  {factor.impact} impact
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Tenant Information */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Tenant Details
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-bg-secondary flex items-center justify-center text-xl">
                👤
              </div>
              <div>
                <div className="font-semibold text-text-primary">{ledgerData.tenant.name}</div>
                <div className="text-sm text-text-muted">{ledgerData.tenant.email}</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border-subtle">
              <div>
                <div className="text-sm text-text-muted">Phone</div>
                <div className="font-medium text-text-primary">{ledgerData.tenant.phone}</div>
              </div>
              <div>
                <div className="text-sm text-text-muted">Weekly Rent</div>
                <div className="font-medium text-text-primary">${ledgerData.property.weekly_rent}</div>
              </div>
              <div>
                <div className="text-sm text-text-muted">Lease Start</div>
                <div className="font-medium text-text-primary">{formatDate(ledgerData.tenant.lease_start)}</div>
              </div>
              <div>
                <div className="text-sm text-text-muted">Lease End</div>
                <div className="font-medium text-text-primary">{formatDate(ledgerData.tenant.lease_end)}</div>
              </div>
            </div>
          </div>
        </Card>

        {/* Payment Reliability */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Payment History (12 months)
          </h3>
          <div className="space-y-4">
            {/* Reliability Score */}
            <div className="flex items-center justify-between p-4 rounded-lg bg-bg-secondary">
              <span className="text-text-secondary">Reliability Score</span>
              <span className={`text-2xl font-bold ${
                ledgerData.payment_history.payment_reliability_score >= 80 ? 'text-success' :
                ledgerData.payment_history.payment_reliability_score >= 60 ? 'text-warning' : 'text-danger'
              }`}>
                {ledgerData.payment_history.payment_reliability_score}%
              </span>
            </div>

            {/* Payment Breakdown */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'On Time', value: ledgerData.payment_history.last_12_months.on_time, color: 'text-success' },
                { label: '1-7 Days Late', value: ledgerData.payment_history.last_12_months.late_1_7_days, color: 'text-warning' },
                { label: '8-14 Days Late', value: ledgerData.payment_history.last_12_months.late_8_14_days, color: 'text-orange-400' },
                { label: '14+ Days Late', value: ledgerData.payment_history.last_12_months.late_14_plus_days, color: 'text-danger' },
              ].map((item) => (
                <div key={item.label} className="p-3 rounded-lg bg-bg-secondary text-center">
                  <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
                  <div className="text-xs text-text-muted">{item.label}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Communication History */}
      <Card variant="default">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Recent Communication
        </h3>
        <div className="space-y-3">
          {breachData.communication_history.map((comm, i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-bg-secondary">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                comm.type === 'SMS' ? 'bg-info/20 text-info' :
                comm.type === 'Email' ? 'bg-accent-primary/20 text-accent-primary' :
                'bg-success/20 text-success'
              }`}>
                {comm.type === 'SMS' ? '💬' : comm.type === 'Email' ? '📧' : '📞'}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <Badge variant="neutral" size="sm">{comm.type}</Badge>
                  <span className="text-sm text-text-muted">{formatDate(comm.date)}</span>
                </div>
                <p className="text-text-primary mt-1">{comm.message}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Compliance Checklist & Breach Notice */}
      <div className="grid grid-cols-2 gap-6">
        {/* Compliance Checklist */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Compliance Checklist
          </h3>
          <div className="space-y-2">
            {riskData.compliance_checklist.map((item, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-bg-secondary">
                {item.status === 'verified' ? (
                  <div className="w-6 h-6 rounded-full bg-success/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                ) : (
                  <div className="w-6 h-6 rounded-full bg-warning/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                )}
                <span className={item.status === 'verified' ? 'text-text-primary' : 'text-warning'}>
                  {item.item}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* Breach Notice Preview */}
        <Card variant="elevated" className="border-danger/20">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Breach Notice Preview
          </h3>
          <div className="p-4 rounded-lg bg-danger/5 border border-danger/20 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              <span className="font-semibold text-danger">{riskData.breach_notice_preview.notice_type}</span>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-3 border-t border-danger/20">
              <div>
                <div className="text-sm text-text-muted">Form Number</div>
                <div className="font-medium text-text-primary">{riskData.breach_notice_preview.form_number}</div>
              </div>
              <div>
                <div className="text-sm text-text-muted">Termination Date</div>
                <div className="font-medium text-text-primary">{formatDate(riskData.breach_notice_preview.termination_date)}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm text-text-muted">Amount to Remedy</div>
                <div className="text-xl font-bold text-danger">{riskData.breach_notice_preview.amount_to_remedy}</div>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 rounded-lg bg-warning/10 border border-warning/20">
            <div className="flex items-center gap-2 text-warning text-sm">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span className="font-medium">Requires HITL Approval</span>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              This notice requires manager approval before being issued to the tenant.
            </p>
          </div>
        </Card>
      </div>

      {/* Action Workflow */}
      <Card variant="elevated" className="border-accent-primary/20">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Recommended Action Workflow
        </h3>
        <div className="grid grid-cols-2 gap-6">
          {/* Immediate Actions */}
          <div>
            <h4 className="font-medium text-text-primary mb-3 flex items-center gap-2">
              <Badge variant="error" size="sm">Immediate</Badge>
              Actions Required
            </h4>
            <div className="space-y-3">
              {riskData.recommended_workflow.immediate.map((item) => (
                <div key={item.step} className="flex items-start gap-3 p-3 rounded-lg bg-bg-secondary">
                  <div className="w-6 h-6 rounded-full bg-accent-primary text-white flex items-center justify-center text-sm font-medium flex-shrink-0">
                    {item.step}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-text-primary">{item.action}</div>
                    <div className="flex items-center gap-2 mt-1 text-sm text-text-muted">
                      <span>👤 {item.assignee}</span>
                      <span>•</span>
                      <span>⏰ {item.deadline}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Follow-up Actions */}
          <div>
            <h4 className="font-medium text-text-primary mb-3 flex items-center gap-2">
              <Badge variant="info" size="sm">Follow-up</Badge>
              Next Steps
            </h4>
            <div className="space-y-3">
              {riskData.recommended_workflow.follow_up.map((item, i) => (
                <div key={i} className="p-3 rounded-lg bg-bg-secondary">
                  <div className="font-medium text-text-primary">{item.action}</div>
                  <div className="text-sm text-text-muted mt-1">Timeline: {item.timeline}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
