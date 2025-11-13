"""
Data Analytics Module for the AI Voice Assistant
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAssistantAnalytics:
    """
    Analytics module for analyzing voice assistant usage patterns and performance.
    """
    
    def __init__(self):
        """
        Initialize the analytics module.
        """
        self.usage_data = pd.DataFrame()
        self.performance_data = pd.DataFrame()
        self.user_data = pd.DataFrame()
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def load_data_from_database(self):
        """
        Load analytics data from Django database models.
        """
        try:
            # Import Django models
            from voice_app.models import VoiceCommand, UserProfile, SystemLog
            
            # Load voice command data
            commands = VoiceCommand.objects.all().values()
            self.usage_data = pd.DataFrame(list(commands))
            
            # Load user profile data
            users = UserProfile.objects.all().values()
            self.user_data = pd.DataFrame(list(users))
            
            # Load system log data
            logs = SystemLog.objects.all().values()
            self.performance_data = pd.DataFrame(list(logs))
            
            logger.info(f"Loaded {len(self.usage_data)} voice commands, {len(self.user_data)} users, {len(self.performance_data)} log entries")
            
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
    
    def generate_usage_statistics(self) -> Dict:
        """
        Generate usage statistics from voice command data.
        
        Returns:
            Dict: Usage statistics
        """
        if self.usage_data.empty:
            return {"error": "No usage data available"}
        
        try:
            stats = {
                "total_commands": len(self.usage_data),
                "unique_users": self.usage_data['user_id'].nunique() if 'user_id' in self.usage_data.columns else 0,
                "date_range": {
                    "start": self.usage_data['created_at'].min().strftime('%Y-%m-%d') if 'created_at' in self.usage_data.columns else "N/A",
                    "end": self.usage_data['created_at'].max().strftime('%Y-%m-%d') if 'created_at' in self.usage_data.columns else "N/A"
                }
            }
            
            # Intent distribution
            if 'intent' in self.usage_data.columns:
                intent_counts = self.usage_data['intent'].value_counts()
                stats["intent_distribution"] = intent_counts.to_dict()
                stats["most_common_intent"] = intent_counts.index[0] if not intent_counts.empty else "N/A"
            
            # Commands per day
            if 'created_at' in self.usage_data.columns:
                self.usage_data['date'] = pd.to_datetime(self.usage_data['created_at']).dt.date
                daily_counts = self.usage_data.groupby('date').size()
                stats["average_daily_commands"] = float(daily_counts.mean())
                stats["peak_daily_commands"] = int(daily_counts.max())
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating usage statistics: {e}")
            return {"error": str(e)}
    
    def analyze_user_engagement(self) -> Dict:
        """
        Analyze user engagement patterns.
        
        Returns:
            Dict: User engagement metrics
        """
        if self.usage_data.empty or self.user_data.empty:
            return {"error": "Insufficient data for engagement analysis"}
        
        try:
            # Merge usage and user data
            if 'user_id' in self.usage_data.columns and 'user_id' in self.user_data.columns:
                merged_data = pd.merge(self.usage_data, self.user_data, on='user_id', how='left')
            else:
                merged_data = self.usage_data
            
            engagement = {
                "total_users": len(self.user_data),
                "active_users": len(merged_data['user_id'].unique()) if 'user_id' in merged_data.columns else 0
            }
            
            # Commands per user
            if 'user_id' in merged_data.columns:
                user_command_counts = merged_data['user_id'].value_counts()
                engagement["avg_commands_per_user"] = float(user_command_counts.mean())
                engagement["most_active_user_commands"] = int(user_command_counts.max())
            
            # User retention (if we have signup dates)
            if 'created_at_x' in merged_data.columns:  # From user profiles
                merged_data['signup_date'] = pd.to_datetime(merged_data['created_at_x']).dt.date
                user_first_commands = merged_data.groupby('user_id')['created_at_y'].min()  # From voice commands
                # Calculate days between signup and first command
                # This is a simplified example - real implementation would be more complex
                
            return engagement
            
        except Exception as e:
            logger.error(f"Error analyzing user engagement: {e}")
            return {"error": str(e)}
    
    def analyze_performance_metrics(self) -> Dict:
        """
        Analyze system performance metrics.
        
        Returns:
            Dict: Performance metrics
        """
        if self.performance_data.empty:
            return {"error": "No performance data available"}
        
        try:
            performance = {
                "total_logs": len(self.performance_data),
                "error_rate": 0.0,
                "warning_rate": 0.0
            }
            
            # Error and warning analysis
            if 'level' in self.performance_data.columns:
                error_logs = self.performance_data[self.performance_data['level'] == 'ERROR']
                warning_logs = self.performance_data[self.performance_data['level'] == 'WARNING']
                
                performance["error_rate"] = len(error_logs) / len(self.performance_data) * 100
                performance["warning_rate"] = len(warning_logs) / len(self.performance_data) * 100
                
                # Most common error messages
                if 'message' in error_logs.columns:
                    common_errors = error_logs['message'].value_counts().head(5)
                    performance["common_errors"] = common_errors.to_dict()
            
            # Processing time analysis (if available)
            if 'processing_time' in self.usage_data.columns:
                performance["avg_processing_time"] = float(self.usage_data['processing_time'].mean())
                performance["max_processing_time"] = float(self.usage_data['processing_time'].max())
                performance["min_processing_time"] = float(self.usage_data['processing_time'].min())
            
            return performance
            
        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {e}")
            return {"error": str(e)}
    
    def create_usage_trends_chart(self) -> Optional[str]:
        """
        Create a usage trends chart.
        
        Returns:
            Optional[str]: Base64 encoded chart image or None
        """
        if self.usage_data.empty or 'created_at' not in self.usage_data.columns:
            return None
        
        try:
            # Prepare data
            self.usage_data['date'] = pd.to_datetime(self.usage_data['created_at']).dt.date
            daily_usage = self.usage_data.groupby('date').size().reset_index(name='commands')
            daily_usage['date'] = pd.to_datetime(daily_usage['date'])
            
            # Create chart
            plt.figure(figsize=(12, 6))
            plt.plot(daily_usage['date'], daily_usage['commands'], marker='o', linewidth=2, markersize=6)
            plt.title('Daily Voice Command Usage Trends', fontsize=16, pad=20)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Number of Commands', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Format dates
            plt.tight_layout()
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Error creating usage trends chart: {e}")
            return None
    
    def create_intent_distribution_chart(self) -> Optional[str]:
        """
        Create an intent distribution chart.
        
        Returns:
            Optional[str]: Base64 encoded chart image or None
        """
        if self.usage_data.empty or 'intent' not in self.usage_data.columns:
            return None
        
        try:
            # Prepare data
            intent_counts = self.usage_data['intent'].value_counts()
            
            # Create chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(np.linspace(0, 1, len(intent_counts)))
            wedges, texts, autotexts = plt.pie(
                intent_counts.values, 
                labels=intent_counts.index, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            plt.title('Voice Command Intent Distribution', fontsize=16, pad=20)
            
            # Save to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Error creating intent distribution chart: {e}")
            return None
    
    def generate_comprehensive_report(self) -> Dict:
        """
        Generate a comprehensive analytics report.
        
        Returns:
            Dict: Comprehensive analytics report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "usage_statistics": self.generate_usage_statistics(),
            "user_engagement": self.analyze_user_engagement(),
            "performance_metrics": self.analyze_performance_metrics(),
            "charts": {
                "usage_trends": self.create_usage_trends_chart(),
                "intent_distribution": self.create_intent_distribution_chart()
            }
        }
        
        return report
    
    def export_report_to_csv(self, filename: str = "voice_assistant_analytics.csv"):
        """
        Export analytics data to CSV files.
        
        Args:
            filename (str): Base filename for exports
        """
        try:
            # Export usage data
            if not self.usage_data.empty:
                usage_filename = filename.replace('.csv', '_usage.csv')
                self.usage_data.to_csv(usage_filename, index=False)
                logger.info(f"Usage data exported to {usage_filename}")
            
            # Export user data
            if not self.user_data.empty:
                user_filename = filename.replace('.csv', '_users.csv')
                self.user_data.to_csv(user_filename, index=False)
                logger.info(f"User data exported to {user_filename}")
            
            # Export performance data
            if not self.performance_data.empty:
                perf_filename = filename.replace('.csv', '_performance.csv')
                self.performance_data.to_csv(perf_filename, index=False)
                logger.info(f"Performance data exported to {perf_filename}")
                
        except Exception as e:
            logger.error(f"Error exporting data to CSV: {e}")


# Example usage
if __name__ == "__main__":
    # Create an instance of the analytics module
    analytics = VoiceAssistantAnalytics()
    
    # In a real application, you would load data from the database
    # analytics.load_data_from_database()
    
    # For demonstration, create some sample data
    sample_usage_data = pd.DataFrame({
        'user_id': [1, 2, 1, 3, 2, 1, 4, 3, 2, 1],
        'intent': ['time_query', 'weather_query', 'news_query', 'time_query', 'weather_query', 
                  'reminder_query', 'music_query', 'navigation_query', 'help_query', 'exit_query'],
        'created_at': pd.date_range('2023-01-01', periods=10, freq='D'),
        'processing_time': [0.5, 1.2, 0.8, 0.3, 1.5, 0.7, 2.1, 1.8, 0.4, 0.2]
    })
    
    sample_user_data = pd.DataFrame({
        'user_id': [1, 2, 3, 4],
        'language': ['en', 'es', 'fr', 'de'],
        'created_at': pd.date_range('2022-12-01', periods=4, freq='D')
    })
    
    sample_performance_data = pd.DataFrame({
        'level': ['INFO', 'ERROR', 'WARNING', 'INFO', 'ERROR'],
        'message': ['Command processed', 'Timeout error', 'High CPU usage', 'User logged in', 'Database connection failed'],
        'timestamp': pd.date_range('2023-01-01', periods=5, freq='H')
    })
    
    # Assign sample data to the analytics instance
    analytics.usage_data = sample_usage_data
    analytics.user_data = sample_user_data
    analytics.performance_data = sample_performance_data
    
    # Generate and print reports
    print("=== Usage Statistics ===")
    usage_stats = analytics.generate_usage_statistics()
    for key, value in usage_stats.items():
        print(f"{key}: {value}")
    
    print("\n=== User Engagement ===")
    engagement = analytics.analyze_user_engagement()
    for key, value in engagement.items():
        print(f"{key}: {value}")
    
    print("\n=== Performance Metrics ===")
    performance = analytics.analyze_performance_metrics()
    for key, value in performance.items():
        print(f"{key}: {value}")