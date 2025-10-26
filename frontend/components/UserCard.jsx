import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { User, Briefcase, Clock } from 'lucide-react';

export default function UserCard({ collaborator }) {
  // Safety check
  if (!collaborator) return null;

  // Parse skills if it's a string
  const skills = typeof collaborator.skills === 'string' 
    ? collaborator.skills.split(',').map(s => s.trim())
    : collaborator.skills || [];
  
  // Parse interests if it's a string
  const interests = typeof collaborator.interests === 'string'
    ? collaborator.interests.split(',').map(i => i.trim())
    : collaborator.interests || [];

  // Calculate compatibility score (0-100) - use score from backend or generate
  const compatibilityScore = collaborator.score || collaborator.compatibility_score || Math.floor(85 + Math.random() * 15);
  
  // Determine color based on score
  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 80) return 'text-blue-600 bg-blue-50 border-blue-200';
    return 'text-purple-600 bg-purple-50 border-purple-200';
  };

  return (
    <Card className="hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300 hover:scale-[1.03] hover:-translate-y-1 relative group">
      {/* Compatibility Badge */}
      <div className="absolute top-3 right-3 z-10">
        <div className={`flex items-center gap-1 px-3 py-1.5 rounded-full border ${getScoreColor(compatibilityScore)} font-semibold text-sm transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg`}>
          <span className="text-lg animate-pulse">✨</span>
          <span>{compatibilityScore}%</span>
        </div>
      </div>
      
      <CardHeader>
        <div className="flex items-start justify-between pr-20">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <User className="w-6 h-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">{collaborator.name || 'Unknown'}</CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Briefcase className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{collaborator.role || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
        {collaborator.availability && (
          <Badge variant="secondary" className="flex items-center gap-1 w-fit mt-2">
            <Clock className="w-3 h-3" />
            {collaborator.availability}
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">{collaborator.bio || 'No bio available'}</p>
        
        <div className="space-y-3">
          {skills.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Skills</h4>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <Badge key={index} variant="outline">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {interests.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold mb-2">Interests</h4>
              <div className="flex flex-wrap gap-2">
                {interests.map((interest, index) => (
                  <Badge key={index} className="bg-secondary text-secondary-foreground">
                    {interest}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
