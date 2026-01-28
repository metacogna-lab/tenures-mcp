import { useState } from 'react';
import { Badge } from '../Badge';
import { Card } from '../Card';

interface DocumentData {
  property_id: string;
  document_count: number;
  documents: {
    id: string;
    name: string;
    type: string;
    url: string;
    last_updated: string;
  }[];
  compliance_summary: {
    total_compliance_docs: number;
    up_to_date: number;
    expiring_soon: number;
    expired: number;
  };
}

interface OCRData {
  processing_summary: {
    documents_processed: number;
    successful: number;
    failed: number;
    total_pages: number;
    processing_time_ms: number;
  };
  extracted_content: {
    document_id: string;
    document_name: string;
    confidence_score: number;
    extracted_text: string;
    key_fields: Record<string, string>;
  }[];
}

interface ExpiryData {
  extraction_timestamp: string;
  total_dates_found: number;
  dates_by_document: {
    document_id: string;
    document_name: string;
    dates: {
      date_type: string;
      date_value: string;
      context: string;
      days_until?: number;
      status?: string;
    }[];
  }[];
  expiry_calendar: {
    date: string;
    document: string;
    days_until: number;
    urgency: string;
  }[];
}

interface AuditData {
  audit_timestamp: string;
  audit_result: {
    overall_status: string;
    confidence_score: number;
    documents_reviewed: number;
    issues_found: number;
    warnings: number;
  };
  compliance_matrix: {
    requirement: string;
    status: string;
    expiry: string;
    action_required: string | null;
  }[];
  upcoming_renewals: {
    document: string;
    expiry_date: string;
    days_until_expiry: number;
    recommended_renewal_date: string;
    estimated_cost: string;
    approved_providers: string[];
  }[];
  audit_summary: {
    last_audit: string;
    next_scheduled_audit: string;
    audit_frequency: string;
    compliance_score: number;
    trend: string;
  };
  recommendations: {
    priority: string;
    action: string;
    deadline: string | null;
  }[];
}

interface ComplianceReportViewProps {
  documentData: DocumentData;
  ocrData: OCRData;
  expiryData: ExpiryData;
  auditData: AuditData;
}

export function ComplianceReportView({ documentData, ocrData, expiryData, auditData }: ComplianceReportViewProps) {
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'documents' | 'timeline'>('overview');

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-AU', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    });
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'text-danger bg-danger/10 border-danger/20';
      case 'medium': return 'text-warning bg-warning/10 border-warning/20';
      case 'normal': return 'text-info bg-info/10 border-info/20';
      default: return 'text-success bg-success/10 border-success/20';
    }
  };

  const getDocTypeIcon = (type: string) => {
    switch (type) {
      case 'compliance': return '📋';
      case 'contract': return '📝';
      case 'report': return '📊';
      case 'legal': return '⚖️';
      case 'insurance': return '🛡️';
      default: return '📄';
    }
  };

  const selectedDocOCR = ocrData.extracted_content.find(d => d.document_id === selectedDoc);
  const selectedDocExpiry = expiryData.dates_by_document.find(d => d.document_id === selectedDoc);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-text-primary">Compliance Audit Report</h2>
            <Badge 
              variant={auditData.audit_result.overall_status === 'COMPLIANT' ? 'success' : 'error'}
              size="md"
            >
              {auditData.audit_result.overall_status}
            </Badge>
          </div>
          <p className="text-text-secondary">Property: {documentData.property_id}</p>
          <p className="text-sm text-text-muted mt-1">
            Audit completed: {formatDate(auditData.audit_timestamp)}
          </p>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold text-success">{auditData.audit_summary.compliance_score}%</div>
          <p className="text-sm text-text-muted">Compliance Score</p>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex items-center gap-2 p-1 bg-bg-secondary rounded-xl w-fit">
        {(['overview', 'documents', 'timeline'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
              viewMode === mode
                ? 'bg-bg-elevated text-text-primary shadow-sm'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {mode}
          </button>
        ))}
      </div>

      {/* Overview View */}
      {viewMode === 'overview' && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Documents Reviewed', value: auditData.audit_result.documents_reviewed, icon: '📁', color: 'text-info' },
              { label: 'Issues Found', value: auditData.audit_result.issues_found, icon: '❌', color: auditData.audit_result.issues_found > 0 ? 'text-danger' : 'text-success' },
              { label: 'Warnings', value: auditData.audit_result.warnings, icon: '⚠️', color: auditData.audit_result.warnings > 0 ? 'text-warning' : 'text-success' },
              { label: 'OCR Confidence', value: `${(auditData.audit_result.confidence_score * 100).toFixed(0)}%`, icon: '🎯', color: 'text-accent-primary' },
            ].map((stat) => (
              <Card key={stat.label} variant="default" padding="md">
                <div className="text-2xl mb-1">{stat.icon}</div>
                <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                <div className="text-sm text-text-muted">{stat.label}</div>
              </Card>
            ))}
          </div>

          {/* Compliance Matrix */}
          <Card variant="default">
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
              Compliance Status Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border-subtle">
                    <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Requirement</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-text-muted">Status</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-text-muted">Expiry Date</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Action Required</th>
                  </tr>
                </thead>
                <tbody>
                  {auditData.compliance_matrix.map((item, i) => (
                    <tr key={i} className="border-b border-border-subtle last:border-0 hover:bg-bg-secondary/50">
                      <td className="py-3 px-4">
                        <span className="font-medium text-text-primary">{item.requirement}</span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant={item.status === 'compliant' ? 'success' : 'error'} size="sm">
                          {item.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center text-text-secondary">
                        {formatDate(item.expiry)}
                      </td>
                      <td className="py-3 px-4 text-text-muted">
                        {item.action_required || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* OCR Processing Summary */}
          <Card variant="default">
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
              Document Processing Summary
            </h3>
            <div className="grid grid-cols-5 gap-4">
              {[
                { label: 'Processed', value: ocrData.processing_summary.documents_processed, color: 'text-info' },
                { label: 'Successful', value: ocrData.processing_summary.successful, color: 'text-success' },
                { label: 'Failed', value: ocrData.processing_summary.failed, color: 'text-danger' },
                { label: 'Total Pages', value: ocrData.processing_summary.total_pages, color: 'text-text-primary' },
                { label: 'Processing Time', value: `${(ocrData.processing_summary.processing_time_ms / 1000).toFixed(1)}s`, color: 'text-accent-primary' },
              ].map((stat) => (
                <div key={stat.label} className="text-center p-4 rounded-lg bg-bg-secondary">
                  <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
                  <div className="text-sm text-text-muted">{stat.label}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* Upcoming Renewals */}
          {auditData.upcoming_renewals.length > 0 && (
            <Card variant="elevated" className="border-warning/20">
              <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
                Upcoming Renewals
              </h3>
              {auditData.upcoming_renewals.map((renewal, i) => (
                <div key={i} className="p-4 rounded-lg bg-warning/5 border border-warning/20">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-text-primary">{renewal.document}</h4>
                      <p className="text-sm text-text-muted mt-1">
                        Expires: {formatDate(renewal.expiry_date)} ({renewal.days_until_expiry} days)
                      </p>
                    </div>
                    <Badge variant="warning" size="md">{renewal.days_until_expiry} days</Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-warning/20">
                    <div>
                      <div className="text-sm text-text-muted">Recommended Renewal</div>
                      <div className="font-medium text-text-primary">{formatDate(renewal.recommended_renewal_date)}</div>
                    </div>
                    <div>
                      <div className="text-sm text-text-muted">Estimated Cost</div>
                      <div className="font-medium text-text-primary">{renewal.estimated_cost}</div>
                    </div>
                    <div>
                      <div className="text-sm text-text-muted">Approved Providers</div>
                      <div className="font-medium text-text-primary">{renewal.approved_providers.length} available</div>
                    </div>
                  </div>
                </div>
              ))}
            </Card>
          )}

          {/* Recommendations */}
          <Card variant="default">
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
              Recommendations
            </h3>
            <div className="space-y-3">
              {auditData.recommendations.map((rec, i) => (
                <div 
                  key={i} 
                  className={`flex items-center gap-4 p-4 rounded-lg border ${
                    rec.priority === 'low' ? 'bg-info/5 border-info/20' :
                    rec.priority === 'info' ? 'bg-bg-secondary border-border-subtle' :
                    'bg-warning/5 border-warning/20'
                  }`}
                >
                  <Badge 
                    variant={rec.priority === 'low' ? 'info' : rec.priority === 'info' ? 'neutral' : 'warning'} 
                    size="md"
                  >
                    {rec.priority}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-text-primary">{rec.action}</p>
                    {rec.deadline && (
                      <p className="text-sm text-text-muted mt-1">Deadline: {formatDate(rec.deadline)}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      {/* Documents View */}
      {viewMode === 'documents' && (
        <div className="grid grid-cols-12 gap-6">
          {/* Document List */}
          <div className="col-span-4 space-y-3">
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider">
              Documents ({documentData.document_count})
            </h3>
            {documentData.documents.map((doc) => {
              const ocrResult = ocrData.extracted_content.find(o => o.document_id === doc.id);
              return (
                <Card 
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc.id)}
                  selected={selectedDoc === doc.id}
                  padding="md"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{getDocTypeIcon(doc.type)}</span>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-text-primary truncate">{doc.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="neutral" size="sm">{doc.type}</Badge>
                        {ocrResult && (
                          <span className="text-xs text-success">
                            {(ocrResult.confidence_score * 100).toFixed(0)}% OCR
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Document Detail */}
          <div className="col-span-8">
            {selectedDoc && selectedDocOCR ? (
              <Card variant="elevated" padding="none">
                <div className="p-4 border-b border-border-subtle bg-bg-tertiary/50">
                  <h3 className="font-semibold text-text-primary">{selectedDocOCR.document_name}</h3>
                  <p className="text-sm text-text-muted">
                    Confidence: {(selectedDocOCR.confidence_score * 100).toFixed(0)}%
                  </p>
                </div>
                
                {/* Extracted Fields */}
                <div className="p-4 border-b border-border-subtle">
                  <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
                    Extracted Information
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(selectedDocOCR.key_fields).map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-bg-secondary">
                        <div className="text-xs text-text-muted capitalize">{key.replace(/_/g, ' ')}</div>
                        <div className="font-medium text-text-primary mt-1">{value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Expiry Dates */}
                {selectedDocExpiry && (
                  <div className="p-4 border-b border-border-subtle">
                    <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
                      Important Dates
                    </h4>
                    <div className="space-y-2">
                      {selectedDocExpiry.dates.map((date, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-bg-secondary">
                          <div>
                            <div className="font-medium text-text-primary capitalize">{date.date_type}</div>
                            <div className="text-sm text-text-muted">{date.context}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-text-primary">{formatDate(date.date_value)}</div>
                            {date.days_until !== undefined && (
                              <div className={`text-sm ${
                                date.days_until < 30 ? 'text-danger' :
                                date.days_until < 90 ? 'text-warning' : 'text-success'
                              }`}>
                                {date.days_until} days
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Raw OCR Text */}
                <div className="p-4">
                  <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
                    Extracted Text
                  </h4>
                  <pre className="p-4 rounded-lg bg-bg-secondary text-sm text-text-secondary font-mono whitespace-pre-wrap max-h-64 overflow-auto">
                    {selectedDocOCR.extracted_text}
                  </pre>
                </div>
              </Card>
            ) : (
              <Card variant="outlined" className="h-full flex items-center justify-center">
                <div className="text-center py-16">
                  <div className="w-16 h-16 rounded-xl bg-bg-tertiary mx-auto mb-4 flex items-center justify-center text-3xl">
                    📄
                  </div>
                  <p className="text-text-muted">Select a document to view details</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Timeline View */}
      {viewMode === 'timeline' && (
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-6">
            Expiry Timeline
          </h3>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border-subtle" />
            
            <div className="space-y-6">
              {expiryData.expiry_calendar.map((item, i) => (
                <div key={i} className="relative flex items-start gap-6 pl-12">
                  {/* Timeline dot */}
                  <div className={`absolute left-4 w-5 h-5 rounded-full border-2 ${
                    item.urgency === 'high' ? 'bg-danger border-danger' :
                    item.urgency === 'medium' ? 'bg-warning border-warning' :
                    item.urgency === 'normal' ? 'bg-info border-info' :
                    'bg-success border-success'
                  }`} />
                  
                  {/* Content */}
                  <div className={`flex-1 p-4 rounded-lg border ${getUrgencyColor(item.urgency)}`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold text-text-primary">{item.document}</h4>
                        <p className="text-sm text-text-muted mt-1">Expires: {formatDate(item.date)}</p>
                      </div>
                      <Badge 
                        variant={
                          item.urgency === 'high' ? 'error' :
                          item.urgency === 'medium' ? 'warning' :
                          item.urgency === 'normal' ? 'info' : 'success'
                        }
                        size="md"
                      >
                        {item.days_until} days
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Audit Summary Footer */}
      <Card variant="default" className="bg-bg-secondary/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-text-muted">Last Audit: </span>
              <span className="text-text-primary font-medium">{formatDate(auditData.audit_summary.last_audit)}</span>
            </div>
            <div>
              <span className="text-text-muted">Next Scheduled: </span>
              <span className="text-text-primary font-medium">{formatDate(auditData.audit_summary.next_scheduled_audit)}</span>
            </div>
            <div>
              <span className="text-text-muted">Frequency: </span>
              <span className="text-text-primary font-medium">{auditData.audit_summary.audit_frequency}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-text-muted">Trend: </span>
            <Badge variant={auditData.audit_summary.trend === 'stable' ? 'success' : 'warning'}>
              {auditData.audit_summary.trend}
            </Badge>
          </div>
        </div>
      </Card>
    </div>
  );
}
