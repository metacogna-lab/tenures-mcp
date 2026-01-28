import { Badge } from '../Badge';
import { Card } from '../Card';

interface VendorReportData {
  report_id: string;
  property_id: string;
  generated_at: string;
  report_type: string;
  executive_summary: {
    headline: string;
    key_metrics: {
      open_home_attendance: string;
      buyer_enquiries: number;
      private_inspections: number;
      days_on_market: number;
    };
    market_position: string;
  };
  feedback_summary: {
    property_id: string;
    total_feedback_entries: number;
    sentiment_breakdown: {
      positive: { count: number; percentage: number };
      neutral: { count: number; percentage: number };
      negative: { count: number; percentage: number };
    };
    category_analysis: Record<string, { sentiment: string; score: number; mentions: number }>;
    top_positive_comments: { comment: string; category: string; date: string }[];
    top_concerns: { concern: string; frequency: number }[];
    buyer_intent_signals: {
      high_interest: number;
      moderate_interest: number;
      just_looking: number;
    };
  };
  market_insights: {
    comparable_sales: { address: string; sold_price: string; sold_date: string }[];
    market_trend: string;
    median_days_on_market: number;
  };
  recommendations: { priority: string; action: string }[];
  next_steps: {
    scheduled_activities: string[];
    vendor_meeting: string;
  };
}

interface PropertyData {
  property_id: string;
  address: {
    street: string;
    suburb: string;
    state: string;
    postcode: string;
  };
  listing: {
    status: string;
    price_guide: string;
    listed_date: string;
    days_on_market: number;
    agent: {
      name: string;
      phone: string;
      email: string;
    };
  };
  property: {
    type: string;
    bedrooms: number;
    bathrooms: number;
    parking: number;
    land_size: string;
    features: string[];
  };
  open_homes: {
    total_held: number;
    total_attendees: number;
    next_scheduled: string;
  };
}

interface VendorReportViewProps {
  reportData: VendorReportData;
  propertyData: PropertyData;
  feedbackData: VendorReportData['feedback_summary'];
}

export function VendorReportView({ reportData, propertyData, feedbackData }: VendorReportViewProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-AU', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    });
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-success';
      case 'neutral': return 'text-warning';
      case 'negative': return 'text-danger';
      default: return 'text-text-secondary';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-danger/10 text-danger border-danger/20';
      case 'medium': return 'bg-warning/10 text-warning border-warning/20';
      case 'low': return 'bg-info/10 text-info border-info/20';
      default: return 'bg-bg-tertiary text-text-secondary border-border-subtle';
    }
  };

  return (
    <div className="space-y-6">
      {/* Report Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-text-primary">Weekly Vendor Report</h2>
            <Badge variant="success">Generated</Badge>
          </div>
          <p className="text-text-secondary">
            {propertyData.address.street}, {propertyData.address.suburb} {propertyData.address.state} {propertyData.address.postcode}
          </p>
          <p className="text-sm text-text-muted mt-1">
            Report ID: {reportData.report_id} • Generated: {formatDate(reportData.generated_at)}
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-accent-primary">{propertyData.listing.price_guide}</div>
          <p className="text-sm text-text-muted">{propertyData.listing.days_on_market} days on market</p>
        </div>
      </div>

      {/* Executive Summary */}
      <Card variant="elevated" className="border-accent-primary/20">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-accent-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-text-primary mb-1">Executive Summary</h3>
            <p className="text-accent-primary font-medium">{reportData.executive_summary.headline}</p>
            <p className="text-sm text-text-secondary mt-2">{reportData.executive_summary.market_position}</p>
          </div>
        </div>
      </Card>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Open Home Attendance', value: reportData.executive_summary.key_metrics.open_home_attendance, icon: '👥' },
          { label: 'Buyer Enquiries', value: reportData.executive_summary.key_metrics.buyer_enquiries, icon: '📧' },
          { label: 'Private Inspections', value: reportData.executive_summary.key_metrics.private_inspections, icon: '🔑' },
          { label: 'Days on Market', value: reportData.executive_summary.key_metrics.days_on_market, icon: '📅' },
        ].map((metric) => (
          <Card key={metric.label} variant="default" padding="md">
            <div className="text-2xl mb-1">{metric.icon}</div>
            <div className="text-2xl font-bold text-text-primary">{metric.value}</div>
            <div className="text-sm text-text-muted">{metric.label}</div>
          </Card>
        ))}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Feedback Sentiment */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Feedback Sentiment Analysis
          </h3>
          <div className="space-y-4">
            {/* Sentiment Bar */}
            <div className="h-4 rounded-full overflow-hidden flex bg-bg-secondary">
              <div 
                className="bg-success h-full transition-all" 
                style={{ width: `${feedbackData.sentiment_breakdown.positive.percentage}%` }}
              />
              <div 
                className="bg-warning h-full transition-all" 
                style={{ width: `${feedbackData.sentiment_breakdown.neutral.percentage}%` }}
              />
              <div 
                className="bg-danger h-full transition-all" 
                style={{ width: `${feedbackData.sentiment_breakdown.negative.percentage}%` }}
              />
            </div>
            
            {/* Legend */}
            <div className="flex justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-success" />
                <span className="text-text-secondary">
                  Positive ({feedbackData.sentiment_breakdown.positive.count}) - {feedbackData.sentiment_breakdown.positive.percentage.toFixed(1)}%
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-warning" />
                <span className="text-text-secondary">
                  Neutral ({feedbackData.sentiment_breakdown.neutral.count})
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-danger" />
                <span className="text-text-secondary">
                  Negative ({feedbackData.sentiment_breakdown.negative.count})
                </span>
              </div>
            </div>

            {/* Total */}
            <div className="text-center pt-2 border-t border-border-subtle">
              <span className="text-2xl font-bold text-text-primary">{feedbackData.total_feedback_entries}</span>
              <span className="text-text-muted ml-2">total feedback entries</span>
            </div>
          </div>
        </Card>

        {/* Buyer Intent */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Buyer Intent Signals
          </h3>
          <div className="space-y-3">
            {[
              { label: 'High Interest', value: feedbackData.buyer_intent_signals.high_interest, color: 'bg-success', total: feedbackData.total_feedback_entries },
              { label: 'Moderate Interest', value: feedbackData.buyer_intent_signals.moderate_interest, color: 'bg-info', total: feedbackData.total_feedback_entries },
              { label: 'Just Looking', value: feedbackData.buyer_intent_signals.just_looking, color: 'bg-text-muted', total: feedbackData.total_feedback_entries },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">{item.label}</span>
                  <span className="font-medium text-text-primary">{item.value} buyers</span>
                </div>
                <div className="h-2 rounded-full bg-bg-secondary overflow-hidden">
                  <div 
                    className={`h-full ${item.color} transition-all`}
                    style={{ width: `${(item.value / item.total) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-border-subtle">
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold text-success">{feedbackData.buyer_intent_signals.high_interest}</span>
              <span className="text-text-secondary">serious buyers identified for follow-up</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Category Analysis */}
      <Card variant="default">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Feedback by Category
        </h3>
        <div className="grid grid-cols-5 gap-4">
          {Object.entries(feedbackData.category_analysis).map(([category, data]) => (
            <div key={category} className="text-center p-4 rounded-lg bg-bg-secondary">
              <div className={`text-3xl font-bold ${getSentimentColor(data.sentiment)}`}>
                {data.score.toFixed(1)}
              </div>
              <div className="text-sm font-medium text-text-primary mt-1 capitalize">{category}</div>
              <div className="text-xs text-text-muted">{data.mentions} mentions</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Comments & Concerns */}
      <div className="grid grid-cols-2 gap-6">
        {/* Top Comments */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Top Positive Feedback
          </h3>
          <div className="space-y-3">
            {feedbackData.top_positive_comments.map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-success/5 border border-success/20">
                <p className="text-text-primary">"{item.comment}"</p>
                <div className="flex items-center gap-2 mt-2 text-xs text-text-muted">
                  <Badge variant="success" size="sm">{item.category}</Badge>
                  <span>{formatDate(item.date)}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Top Concerns */}
        <Card variant="default">
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
            Common Concerns to Address
          </h3>
          <div className="space-y-3">
            {feedbackData.top_concerns.map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-danger/5 border border-danger/20">
                <div className="flex items-start justify-between">
                  <p className="text-text-primary">{item.concern}</p>
                  <Badge variant="error" size="sm">{item.frequency}x</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Market Insights */}
      <Card variant="default">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Comparable Sales
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border-subtle">
                <th className="text-left py-3 px-4 text-sm font-medium text-text-muted">Address</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-text-muted">Sold Price</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-text-muted">Sold Date</th>
              </tr>
            </thead>
            <tbody>
              {reportData.market_insights.comparable_sales.map((sale, i) => (
                <tr key={i} className="border-b border-border-subtle last:border-0">
                  <td className="py-3 px-4 text-text-primary">{sale.address}</td>
                  <td className="py-3 px-4 text-right font-semibold text-success">{sale.sold_price}</td>
                  <td className="py-3 px-4 text-right text-text-muted">{formatDate(sale.sold_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 pt-4 border-t border-border-subtle flex items-center justify-between">
          <div>
            <span className="text-text-muted">Market Trend: </span>
            <span className="text-text-primary font-medium">{reportData.market_insights.market_trend}</span>
          </div>
          <div>
            <span className="text-text-muted">Median Days on Market: </span>
            <span className="text-text-primary font-medium">{reportData.market_insights.median_days_on_market} days</span>
          </div>
        </div>
      </Card>

      {/* Recommendations */}
      <Card variant="default">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Recommended Actions
        </h3>
        <div className="space-y-3">
          {reportData.recommendations.map((rec, i) => (
            <div 
              key={i} 
              className={`flex items-center gap-4 p-4 rounded-lg border ${getPriorityColor(rec.priority)}`}
            >
              <div className="flex-shrink-0">
                <Badge variant={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'info'} size="md">
                  {rec.priority}
                </Badge>
              </div>
              <p className="text-text-primary">{rec.action}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Next Steps */}
      <Card variant="elevated" className="border-accent-primary/20">
        <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-4">
          Next Steps
        </h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-text-primary mb-3">Scheduled Activities</h4>
            <ul className="space-y-2">
              {reportData.next_steps.scheduled_activities.map((activity, i) => (
                <li key={i} className="flex items-center gap-2 text-text-secondary">
                  <svg className="w-4 h-4 text-accent-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {activity}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-text-primary mb-3">Vendor Communication</h4>
            <p className="text-text-secondary">{reportData.next_steps.vendor_meeting}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
