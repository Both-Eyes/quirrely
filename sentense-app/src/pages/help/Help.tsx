import { useState } from 'react';
import {
  HelpCircle,
  BookOpen,
  MessageCircle,
  Mail,
  ChevronDown,
  ChevronUp,
  Search,
  ExternalLink,
  Zap,
  Shield,
  CreditCard,
  User,
  PenTool,
  Sparkles,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input } from '@/components/ui';

// FAQ Data
const faqCategories = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: <Zap className="h-5 w-5" />,
    faqs: [
      {
        question: 'What is Quirrely?',
        answer: 'Quirrely is a literary voice analysis platform that helps writers discover and develop their unique writing voice. Using advanced AI analysis, we identify your voice patterns, style characteristics, and provide personalized insights to help you grow as a writer.',
      },
      {
        question: 'How do I analyze my writing?',
        answer: 'Simply paste your writing sample (at least 500 words for best results) into the analysis tool on your dashboard. Our AI will analyze your voice patterns, style markers, and provide a detailed breakdown of your writing characteristics.',
      },
      {
        question: 'What countries is Quirrely available in?',
        answer: 'Quirrely is currently available in Canada, United Kingdom, Australia, and New Zealand. We\'re focused on serving Commonwealth English writers to ensure the highest quality voice analysis.',
      },
      {
        question: 'Is there a free trial?',
        answer: 'Yes! When you sign up, you get a 14-day free trial of Pro features. You can analyze unlimited samples, save your results, and explore all Pro features before deciding to subscribe.',
      },
    ],
  },
  {
    id: 'voice-analysis',
    title: 'Voice Analysis',
    icon: <Sparkles className="h-5 w-5" />,
    faqs: [
      {
        question: 'What is a voice profile?',
        answer: 'Your voice profile is a comprehensive analysis of your writing style. It includes your primary and secondary voice types, dimension scores (assertiveness, formality, detail, poeticism, openness, dynamism), and AI-generated insights about your unique voice.',
      },
      {
        question: 'How accurate is the analysis?',
        answer: 'Our analysis is powered by advanced language models trained on millions of writing samples. Accuracy improves with more text - we recommend at least 1,000 words for the most accurate profile. Your confidence score indicates how reliable the analysis is.',
      },
      {
        question: 'What are voice dimensions?',
        answer: 'Voice dimensions are the six key characteristics we measure: Assertiveness (confident vs. tentative), Formality (professional vs. casual), Detail (comprehensive vs. concise), Poeticism (lyrical vs. direct), Openness (personal vs. reserved), and Dynamism (energetic vs. measured).',
      },
      {
        question: 'Can my voice profile change over time?',
        answer: 'Absolutely! Your writing voice naturally evolves. With the Voice + Style addon, you can track your voice evolution over time and see how your style develops as you grow as a writer.',
      },
    ],
  },
  {
    id: 'account',
    title: 'Account & Profile',
    icon: <User className="h-5 w-5" />,
    faqs: [
      {
        question: 'How do I change my password?',
        answer: 'Go to Settings > Account > Change Password. Enter your current password and your new password twice to confirm. You\'ll receive an email confirmation once updated.',
      },
      {
        question: 'Can I change my email address?',
        answer: 'Yes, go to Settings > Account > Email. Enter your new email address and we\'ll send a verification link. Your account will be updated once you confirm the new email.',
      },
      {
        question: 'How do I delete my account?',
        answer: 'Go to Settings > Account > Delete Account. This action is permanent and will delete all your data including voice profiles, analyses, and saved content. We\'ll ask you to confirm before proceeding.',
      },
    ],
  },
  {
    id: 'subscription',
    title: 'Subscription & Billing',
    icon: <CreditCard className="h-5 w-5" />,
    faqs: [
      {
        question: 'What are the subscription options?',
        answer: 'We offer Pro subscription at $2.99/month or $30/year (save 16%). The Voice + Style addon is available for $4.99/month or $49.99/year for deeper voice analysis and evolution tracking.',
      },
      {
        question: 'How do I cancel my subscription?',
        answer: 'Go to Settings > Subscription > Cancel. Your access continues until the end of your current billing period. You can resubscribe anytime without losing your data.',
      },
      {
        question: 'What payment methods do you accept?',
        answer: 'We accept all major credit cards (Visa, Mastercard, American Express) and debit cards. Payments are processed securely through Stripe.',
      },
      {
        question: 'Do you offer refunds?',
        answer: 'Yes, we offer a 7-day money-back guarantee for new subscriptions. Contact support@quirrely.com within 7 days of your first payment for a full refund.',
      },
    ],
  },
  {
    id: 'privacy',
    title: 'Privacy & Security',
    icon: <Shield className="h-5 w-5" />,
    faqs: [
      {
        question: 'Is my writing data secure?',
        answer: 'Yes, absolutely. We use industry-standard encryption for all data in transit and at rest. Your writing samples are only used to generate your voice profile and are never shared with third parties.',
      },
      {
        question: 'Do you use my writing to train AI?',
        answer: 'No. Your writing samples are used solely to analyze your voice and are not used to train our AI models. Your creative work remains yours.',
      },
      {
        question: 'Can others see my voice profile?',
        answer: 'By default, your voice profile is private. You can choose to share it publicly on your writer profile, or share individual analysis results via a private link.',
      },
    ],
  },
  {
    id: 'writing',
    title: 'Writing & Content',
    icon: <PenTool className="h-5 w-5" />,
    faqs: [
      {
        question: 'What\'s the minimum text length for analysis?',
        answer: 'We recommend at least 500 words for a basic analysis and 1,000+ words for the most accurate voice profile. Shorter samples may result in lower confidence scores.',
      },
      {
        question: 'Can I analyze different types of writing?',
        answer: 'Yes! You can analyze any type of prose writing - fiction, non-fiction, essays, blog posts, etc. The analysis works best with natural prose rather than poetry or heavily formatted text.',
      },
      {
        question: 'How many analyses can I save?',
        answer: 'Free users can save up to 3 analyses. Pro subscribers get unlimited saved analyses with full history and comparison features.',
      },
    ],
  },
];

// Contact options
const contactOptions = [
  {
    icon: <Mail className="h-6 w-6" />,
    title: 'Email Support',
    description: 'Get help via email within 24 hours',
    action: 'support@quirrely.com',
    href: 'mailto:support@quirrely.com',
  },
  {
    icon: <MessageCircle className="h-6 w-6" />,
    title: 'Community',
    description: 'Join our writer community on Discord',
    action: 'Join Discord',
    href: 'https://discord.gg/quirrely',
  },
  {
    icon: <BookOpen className="h-6 w-6" />,
    title: 'Documentation',
    description: 'Read our detailed guides and tutorials',
    action: 'View Docs',
    href: '/docs',
  },
];

// FAQ Item component
const FAQItem = ({ question, answer }: { question: string; answer: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-gray-200 dark:border-gray-700 last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full py-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 px-4 -mx-4 rounded-lg transition-colors"
      >
        <span className="font-medium text-gray-900 dark:text-white pr-4">{question}</span>
        {isOpen ? (
          <ChevronUp className="h-5 w-5 text-gray-500 flex-shrink-0" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-500 flex-shrink-0" />
        )}
      </button>
      {isOpen && (
        <div className="pb-4 text-gray-600 dark:text-gray-400 animate-in fade-in slide-in-from-bottom duration-200">
          {answer}
        </div>
      )}
    </div>
  );
};

export const Help = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('getting-started');

  // Filter FAQs based on search
  const filteredCategories = searchQuery
    ? faqCategories.map((cat) => ({
        ...cat,
        faqs: cat.faqs.filter(
          (faq) =>
            faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
        ),
      })).filter((cat) => cat.faqs.length > 0)
    : faqCategories;

  const activeData = filteredCategories.find((c) => c.id === activeCategory) || filteredCategories[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-coral-100 dark:bg-coral-900/30 rounded-full mb-4">
          <HelpCircle className="h-8 w-8 text-coral-500" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Help & Support
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Find answers to common questions or get in touch with our team
        </p>
      </div>

      {/* Search */}
      <div className="max-w-xl mx-auto">
        <Input
          placeholder="Search for help..."
          leftIcon={<Search className="h-5 w-5" />}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Contact Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
        {contactOptions.map((option) => (
          <Card key={option.title} className="text-center hover:shadow-lg transition-shadow">
            <CardContent className="py-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-coral-100 dark:bg-coral-900/30 rounded-full mb-3">
                <span className="text-coral-500">{option.icon}</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {option.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                {option.description}
              </p>
              <a
                href={option.href}
                className="inline-flex items-center gap-1 text-coral-500 hover:text-coral-600 font-medium text-sm"
              >
                {option.action}
                <ExternalLink className="h-4 w-4" />
              </a>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="max-w-4xl mx-auto">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          Frequently Asked Questions
        </h2>

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Category Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <nav className="space-y-1">
              {filteredCategories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeCategory === category.id
                      ? 'bg-coral-500 text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  {category.icon}
                  <span className="font-medium">{category.title}</span>
                  <span className={`ml-auto text-sm ${
                    activeCategory === category.id ? 'text-white/70' : 'text-gray-400'
                  }`}>
                    {category.faqs.length}
                  </span>
                </button>
              ))}
            </nav>
          </div>

          {/* FAQ Content */}
          <Card className="flex-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {activeData?.icon}
                {activeData?.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activeData?.faqs.length ? (
                <div className="space-y-0">
                  {activeData.faqs.map((faq, i) => (
                    <FAQItem key={i} question={faq.question} answer={faq.answer} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No results found for "{searchQuery}"
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Still need help */}
      <Card className="max-w-2xl mx-auto bg-gradient-to-br from-coral-50 to-amber-50 dark:from-coral-950/30 dark:to-amber-950/30 border-coral-200 dark:border-coral-800">
        <CardContent className="py-8 text-center">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Still need help?
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Our support team is ready to assist you with any questions
          </p>
          <Button
            onClick={() => window.location.href = 'mailto:support@quirrely.com'}
            leftIcon={<Mail className="h-4 w-4" />}
          >
            Contact Support
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default Help;
