/**
 * @fileoverview LLM Models FAQ Page
 *
 * Provides comprehensive information about available AI models
 * to help users choose the right model for their needs.
 *
 * @module features/settings/pages/LlmFaqPage
 */

import { Link } from 'react-router-dom';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Container,
  Heading,
  Text,
  Badge,
  Button,
} from '@/shared/components';

/**
 * Model info type for display
 */
interface ModelInfo {
  id: string;
  name: string;
  tier: 'flagship' | 'balanced' | 'fast' | 'legacy';
  description: string;
  bestFor: string[];
  notIdealFor?: string[];
  pricing?: string;
}

/**
 * Provider info with models
 */
interface ProviderInfo {
  name: string;
  provider: string;
  description: string;
  models: ModelInfo[];
}

/**
 * All available providers and their models
 */
const PROVIDERS: ProviderInfo[] = [
  {
    name: 'Anthropic Claude',
    provider: 'anthropic',
    description:
      'Claude models excel at nuanced reasoning, coding, and following complex instructions. Known for being helpful, harmless, and honest.',
    models: [
      {
        id: 'claude-opus-4-6',
        name: 'Claude Opus 4.6',
        tier: 'flagship',
        description:
          'The most intelligent Claude model. Exceptional at complex reasoning, research, and tasks requiring deep analysis.',
        bestFor: [
          'Complex research and analysis',
          'Multi-step reasoning problems',
          'Detailed code reviews',
          'Academic or technical writing',
          'Tasks requiring nuanced judgment',
        ],
        notIdealFor: ['High-volume, simple tasks', 'Cost-sensitive applications'],
        pricing: 'Premium tier',
      },
      {
        id: 'claude-sonnet-4-5-20250929',
        name: 'Claude Sonnet 4.5',
        tier: 'balanced',
        description:
          'Best balance of speed and intelligence. Excellent for everyday coding, CV analysis, and general tasks.',
        bestFor: [
          'CV screening and evaluation',
          'Code generation and debugging',
          'Document summarization',
          'General Q&A and chat',
          'Most production workloads',
        ],
        pricing: 'Standard tier',
      },
      {
        id: 'claude-haiku-4-5-20251001',
        name: 'Claude Haiku 4.5',
        tier: 'fast',
        description:
          'Fastest Claude model with excellent intelligence. Ideal for high-volume screening and quick responses.',
        bestFor: [
          'High-volume CV screening',
          'Quick document parsing',
          'Real-time chat responses',
          'Cost-sensitive applications',
          'Simple classification tasks',
        ],
        pricing: 'Economy tier',
      },
      {
        id: 'claude-opus-4-20250514',
        name: 'Claude Opus 4',
        tier: 'legacy',
        description: 'Previous generation flagship. Still excellent for complex tasks.',
        bestFor: ['Complex analysis', 'Research tasks'],
        pricing: 'Premium tier',
      },
      {
        id: 'claude-sonnet-4-20250514',
        name: 'Claude Sonnet 4',
        tier: 'legacy',
        description: 'Previous generation balanced model.',
        bestFor: ['General tasks', 'Coding'],
        pricing: 'Standard tier',
      },
    ],
  },
  {
    name: 'OpenAI GPT',
    provider: 'openai',
    description:
      'GPT models are known for versatility and strong performance across many tasks. The GPT-5 series represents the latest frontier capabilities.',
    models: [
      {
        id: 'gpt-5.2',
        name: 'GPT-5.2',
        tier: 'flagship',
        description:
          'Best OpenAI model for coding and agentic tasks. Top performance across all benchmarks.',
        bestFor: [
          'Complex coding tasks',
          'Agentic workflows',
          'Multi-step reasoning',
          'Technical documentation',
          'Advanced analysis',
        ],
        pricing: 'Premium tier',
      },
      {
        id: 'gpt-5.2-pro',
        name: 'GPT-5.2 Pro',
        tier: 'flagship',
        description: 'Enhanced version of GPT-5.2 with smarter, more precise responses.',
        bestFor: [
          'When you need extra precision',
          'Critical decision-making',
          'Detailed technical analysis',
        ],
        pricing: 'Premium+ tier',
      },
      {
        id: 'gpt-5',
        name: 'GPT-5',
        tier: 'balanced',
        description:
          'Intelligent reasoning model with configurable effort. Great balance of capability and speed.',
        bestFor: [
          'CV evaluation',
          'Document analysis',
          'Coding assistance',
          'General reasoning tasks',
        ],
        pricing: 'Standard tier',
      },
      {
        id: 'gpt-5-mini',
        name: 'GPT-5 Mini',
        tier: 'balanced',
        description: 'Faster, more cost-efficient version of GPT-5 for well-defined tasks.',
        bestFor: [
          'Structured tasks',
          'Template-based generation',
          'Quick analysis',
          'Production workloads',
        ],
        pricing: 'Economy tier',
      },
      {
        id: 'gpt-5-nano',
        name: 'GPT-5 Nano',
        tier: 'fast',
        description: 'Fastest and most cost-efficient GPT-5 variant.',
        bestFor: [
          'High-volume processing',
          'Simple classification',
          'Quick responses',
          'Cost-sensitive apps',
        ],
        pricing: 'Budget tier',
      },
      {
        id: 'gpt-4.1',
        name: 'GPT-4.1',
        tier: 'legacy',
        description: 'Smartest non-reasoning model. Reliable and well-tested.',
        bestFor: ['General tasks', 'When reasoning models are overkill'],
        pricing: 'Standard tier',
      },
      {
        id: 'o3',
        name: 'o3',
        tier: 'flagship',
        description: 'Advanced reasoning model optimized for complex problem-solving.',
        bestFor: ['Math problems', 'Logic puzzles', 'Code debugging', 'Complex reasoning'],
        pricing: 'Premium tier',
      },
      {
        id: 'o4-mini',
        name: 'o4-mini',
        tier: 'balanced',
        description: 'Cost-effective reasoning model.',
        bestFor: ['Reasoning tasks on a budget', 'Structured problem-solving'],
        pricing: 'Economy tier',
      },
    ],
  },
  {
    name: 'Google Gemini',
    provider: 'gemini',
    description:
      'Gemini models offer excellent multimodal capabilities and competitive pricing. Strong for agentic and high-throughput use cases.',
    models: [
      {
        id: 'gemini-3-pro',
        name: 'Gemini 3 Pro',
        tier: 'flagship',
        description:
          'Most intelligent Gemini model. State-of-the-art multimodal understanding and agentic capabilities.',
        bestFor: [
          'Complex multimodal tasks',
          'Agentic workflows',
          'Deep analysis',
          'Research applications',
        ],
        pricing: 'Premium tier',
      },
      {
        id: 'gemini-3-flash',
        name: 'Gemini 3 Flash',
        tier: 'balanced',
        description:
          'Most balanced Gemini model. Built for speed, scale, and frontier intelligence.',
        bestFor: [
          'Production workloads',
          'Balanced performance',
          'Scalable applications',
          'General-purpose tasks',
        ],
        pricing: 'Standard tier',
      },
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro',
        tier: 'balanced',
        description:
          'Advanced thinking model for complex reasoning in code, math, and STEM. Excellent long context support.',
        bestFor: [
          'Complex code analysis',
          'Mathematical reasoning',
          'STEM research',
          'Large document analysis',
        ],
        pricing: 'Standard tier',
      },
      {
        id: 'gemini-2.5-flash',
        name: 'Gemini 2.5 Flash',
        tier: 'balanced',
        description:
          'Best price-performance in the Gemini family. Great for large-scale processing.',
        bestFor: [
          'High-volume CV screening',
          'Large-scale processing',
          'Cost-effective production',
          'Agentic use cases',
        ],
        pricing: 'Economy tier',
      },
      {
        id: 'gemini-2.5-flash-lite',
        name: 'Gemini 2.5 Flash-Lite',
        tier: 'fast',
        description: 'Fastest Gemini model, optimized for cost-efficiency and high throughput.',
        bestFor: ['Maximum throughput', 'Simple tasks', 'Cost-sensitive applications'],
        pricing: 'Budget tier',
      },
    ],
  },
];

/**
 * Get badge variant based on model tier
 */
const getTierBadge = (tier: ModelInfo['tier']) => {
  switch (tier) {
    case 'flagship':
      return { variant: 'success' as const, label: '🚀 Flagship' };
    case 'balanced':
      return { variant: 'info' as const, label: '⚖️ Balanced' };
    case 'fast':
      return { variant: 'warning' as const, label: '⚡ Fast' };
    case 'legacy':
      return { variant: 'neutral' as const, label: '📦 Legacy' };
  }
};

/**
 * LLM FAQ Page Component
 */
export const LlmFaqPage = () => {
  return (
    <Container size="lg" className="py-8">
      {/* Header */}
      <div className="mb-8">
        <Link to="/settings">
          <Button variant="ghost" size="sm" className="mb-4">
            ← Back to Settings
          </Button>
        </Link>
        <Heading level={1} className="mb-2">
          AI Models Guide
        </Heading>
        <Text color="muted" size="lg">
          Learn about available AI models to choose the right one for your needs.
        </Text>
      </div>

      {/* Quick Recommendations */}
      <Card padding="md" className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle>💡 Quick Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <Text weight="semibold" className="mb-2">
                🎯 Best for CV Screening
              </Text>
              <Text size="sm" color="muted">
                <strong>Claude Sonnet 4.5</strong> or <strong>GPT-5</strong> - Great balance of accuracy and speed for evaluating resumes.
              </Text>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <Text weight="semibold" className="mb-2">
                💰 Best Value
              </Text>
              <Text size="sm" color="muted">
                <strong>Gemini 2.5 Flash</strong> or <strong>Claude Haiku 4.5</strong> - Excellent quality at lower cost for high-volume screening.
              </Text>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
              <Text weight="semibold" className="mb-2">
                🧠 Best Intelligence
              </Text>
              <Text size="sm" color="muted">
                <strong>Claude Opus 4.6</strong> or <strong>GPT-5.2 Pro</strong> - Maximum capability for complex analysis.
              </Text>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FAQ Section */}
      <Card padding="md" className="mb-8">
        <CardHeader>
          <CardTitle>❓ Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Text weight="semibold" className="mb-1">
              Why do I need an OpenAI API key even if I use Claude or Gemini?
            </Text>
            <Text size="sm" color="muted">
              OpenAI provides the embeddings (vector representations) used for semantic search and RAG. This is separate from the LLM used for evaluation and chat. Embeddings are very cheap (~$0.0001 per 1K tokens).
            </Text>
          </div>
          <div>
            <Text weight="semibold" className="mb-1">
              What's the difference between flagship and balanced models?
            </Text>
            <Text size="sm" color="muted">
              Flagship models offer maximum intelligence but are slower and more expensive. Balanced models provide excellent quality at reasonable speed and cost - ideal for most production use cases like CV screening.
            </Text>
          </div>
          <div>
            <Text weight="semibold" className="mb-1">
              Can I use different models for different agents?
            </Text>
            <Text size="sm" color="muted">
              Yes! In Settings → LLM Preferences, you can set a default model and override it per agent. For example, use a fast model for parsing and a smarter model for scoring.
            </Text>
          </div>
          <div>
            <Text weight="semibold" className="mb-1">
              Which model is most accurate for CV evaluation?
            </Text>
            <Text size="sm" color="muted">
              Claude Sonnet 4.5 and GPT-5 both provide excellent accuracy for CV screening. For critical hiring decisions, Claude Opus 4.6 or GPT-5.2 Pro offer maximum precision.
            </Text>
          </div>
        </CardContent>
      </Card>

      {/* Provider Sections */}
      {PROVIDERS.map((provider) => (
        <Card key={provider.provider} padding="md" className="mb-6">
          <CardHeader>
            <CardTitle className="text-xl">{provider.name}</CardTitle>
            <CardDescription>{provider.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {provider.models.map((model) => {
                const tierBadge = getTierBadge(model.tier);
                return (
                  <div
                    key={model.id}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <Text weight="semibold">{model.name}</Text>
                      <Badge variant={tierBadge.variant} size="sm">
                        {tierBadge.label}
                      </Badge>
                      {model.pricing && (
                        <Badge variant="neutral" size="sm">
                          {model.pricing}
                        </Badge>
                      )}
                    </div>
                    <Text size="sm" color="muted" className="mb-3">
                      {model.description}
                    </Text>
                    <div className="flex flex-wrap gap-4">
                      <div>
                        <Text size="xs" weight="medium" className="text-green-600 dark:text-green-400 mb-1">
                          ✅ Best For:
                        </Text>
                        <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-0.5">
                          {model.bestFor.map((use, i) => (
                            <li key={i}>• {use}</li>
                          ))}
                        </ul>
                      </div>
                      {model.notIdealFor && (
                        <div>
                          <Text size="xs" weight="medium" className="text-amber-600 dark:text-amber-400 mb-1">
                            ⚠️ Not Ideal For:
                          </Text>
                          <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-0.5">
                            {model.notIdealFor.map((use, i) => (
                              <li key={i}>• {use}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    <Text size="xs" color="muted" className="mt-2 font-mono">
                      Model ID: {model.id}
                    </Text>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Footer CTA */}
      <div className="text-center py-6">
        <Text color="muted" className="mb-4">
          Ready to configure your AI models?
        </Text>
        <Link to="/settings">
          <Button variant="primary">Go to Settings</Button>
        </Link>
      </div>
    </Container>
  );
};

export default LlmFaqPage;
