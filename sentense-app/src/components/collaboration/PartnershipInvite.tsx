import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Badge } from '../ui/Badge';
import { Heart, Users, Briefcase, Palette, Home, Send, UserPlus } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP TYPES
// ═══════════════════════════════════════════════════════════════════════════

const PARTNERSHIP_TYPES = [
  {
    value: 'heart',
    label: 'Heart Partnership',
    icon: Heart,
    description: 'For life\'s most meaningful moments',
    examples: 'Wedding vows, family stories, letters to children, eulogies',
    color: 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100',
  },
  {
    value: 'growth',
    label: 'Growth Partnership',
    icon: Users,
    description: 'Supporting each other\'s journey',
    examples: 'Mentorship, accountability partners, creative challenges',
    color: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100',
  },
  {
    value: 'professional',
    label: 'Professional Partnership',
    icon: Briefcase,
    description: 'Authentic voice at work',
    examples: 'Presentations, proposals, performance reviews',
    color: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100',
  },
  {
    value: 'creative',
    label: 'Creative Partnership',
    icon: Palette,
    description: 'Playing with possibilities together',
    examples: 'Fiction, poetry, blogs, creative experiments',
    color: 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100',
  },
  {
    value: 'life',
    label: 'Life Partnership',
    icon: Home,
    description: 'Getting important things done',
    examples: 'Family planning, community projects, legacy documentation',
    color: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100',
  },
] as const;

type PartnershipType = typeof PARTNERSHIP_TYPES[number]['value'];

// ═══════════════════════════════════════════════════════════════════════════
// INVITATION FORM COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface PartnershipInviteProps {
  onInvite: (invitation: {
    email: string;
    partnership_name: string;
    partnership_intention: string;
    partnership_type: PartnershipType;
  }) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

export const PartnershipInvite: React.FC<PartnershipInviteProps> = ({
  onInvite,
  isLoading = false,
  className = '',
}) => {
  const [step, setStep] = useState<'type' | 'details'>('type');
  const [selectedType, setSelectedType] = useState<PartnershipType | null>(null);
  const [email, setEmail] = useState('');
  const [partnershipName, setPartnershipName] = useState('');
  const [partnershipIntention, setPartnershipIntention] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const selectedPartnership = PARTNERSHIP_TYPES.find(p => p.value === selectedType);

  const handleTypeSelect = (type: PartnershipType) => {
    setSelectedType(type);
    setStep('details');
    setErrors({});
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!partnershipName.trim()) {
      newErrors.partnershipName = 'Partnership name is required';
    } else if (partnershipName.trim().length < 5) {
      newErrors.partnershipName = 'Partnership name must be at least 5 characters';
    }

    if (partnershipIntention.trim().length > 2000) {
      newErrors.partnershipIntention = 'Intention must be less than 2000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedType || !validateForm()) {
      return;
    }

    try {
      await onInvite({
        email: email.trim(),
        partnership_name: partnershipName.trim(),
        partnership_intention: partnershipIntention.trim(),
        partnership_type: selectedType,
      });

      // Reset form on success
      setStep('type');
      setSelectedType(null);
      setEmail('');
      setPartnershipName('');
      setPartnershipIntention('');
      setErrors({});
    } catch (error) {
      console.error('Failed to send invitation:', error);
    }
  };

  const handleBack = () => {
    setStep('type');
    setErrors({});
  };

  if (step === 'type') {
    return (
      <Card className={className} variant="elevated">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-coral-50 dark:bg-coral-950 rounded-lg">
              <UserPlus className="h-5 w-5 text-coral-600 dark:text-coral-400" />
            </div>
            <div>
              <CardTitle className="text-xl text-gray-900 dark:text-gray-100">
                🌸 Invite Your Writing Partner
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Choose the type of partnership that resonates with your heart
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-3">
            {PARTNERSHIP_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.value}
                  onClick={() => handleTypeSelect(type.value)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 ${type.color}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm mb-1">
                        {type.label}
                      </div>
                      <div className="text-xs opacity-80 mb-2">
                        {type.description}
                      </div>
                      <div className="text-xs opacity-70">
                        {type.examples}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className} variant="elevated">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg border ${selectedPartnership?.color}`}>
              {selectedPartnership && <selectedPartnership.icon className="h-5 w-5" />}
            </div>
            <div>
              <CardTitle className="text-xl text-gray-900 dark:text-gray-100">
                {selectedPartnership?.label}
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {selectedPartnership?.description}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={handleBack}>
            Change Type
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Partner Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Who would you love to write with? 💕
            </label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="partner@example.com"
              className={errors.email ? 'border-red-300' : ''}
            />
            {errors.email && (
              <p className="text-red-600 text-sm mt-1">{errors.email}</p>
            )}
          </div>

          {/* Partnership Name */}
          <div>
            <label htmlFor="partnershipName" className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              What would you like to create together? ✨
            </label>
            <Input
              id="partnershipName"
              value={partnershipName}
              onChange={(e) => setPartnershipName(e.target.value)}
              placeholder="e.g., Mom's Memory Book, Our Wedding Vows, The Presentation That Matters"
              maxLength={200}
              className={errors.partnershipName ? 'border-red-300' : ''}
            />
            {errors.partnershipName && (
              <p className="text-red-600 text-sm mt-1">{errors.partnershipName}</p>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {partnershipName.length}/200 characters
            </p>
          </div>

          {/* Partnership Intention */}
          <div>
            <label htmlFor="partnershipIntention" className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
              Share your vision (optional) 🌟
            </label>
            <textarea
              id="partnershipIntention"
              value={partnershipIntention}
              onChange={(e) => setPartnershipIntention(e.target.value)}
              placeholder="What do you hope to discover or create together? This helps your partner understand your shared journey..."
              rows={3}
              maxLength={2000}
              className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-coral-500 focus:border-transparent dark:bg-gray-800 dark:text-gray-100 ${
                errors.partnershipIntention ? 'border-red-300' : ''
              }`}
            />
            {errors.partnershipIntention && (
              <p className="text-red-600 text-sm mt-1">{errors.partnershipIntention}</p>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {partnershipIntention.length}/2000 characters
            </p>
          </div>

          {/* What They'll Get */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
              What your partner will receive:
            </h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-coral-500 rounded-full"></div>
                A secure, private invitation to write together
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-coral-500 rounded-full"></div>
                25,000 word shared creative space (12.5k from each partner)
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-coral-500 rounded-full"></div>
                12,500 words for their own solo discoveries
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-coral-500 rounded-full"></div>
                A supportive space for vulnerable creative expression
              </li>
            </ul>
          </div>

          <div className="flex gap-3 pt-4">
            <Button 
              type="submit" 
              variant="primary" 
              isLoading={isLoading}
              leftIcon={<Send className="h-4 w-4" />}
              className="flex-1"
            >
              {isLoading ? 'Sending Invitation...' : 'Send Partnership Invitation'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default PartnershipInvite;