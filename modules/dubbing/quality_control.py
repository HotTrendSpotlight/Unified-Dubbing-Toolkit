"""
Quality control and validation for dubbing outputs
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path


class QualityController:
    """Quality control for dubbing outputs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_dubbing_output(self, original_file: str, dubbed_file: str) -> Dict[str, Any]:
        """
        Validate the quality of dubbing output
        
        Returns:
            Dict with validation results and quality metrics
        """
        self.logger.info(f"Validating dubbing output: {dubbed_file}")
        
        results = {
            "valid": True,
            "issues": [],
            "metrics": {},
            "recommendations": []
        }
        
        try:
            # Check file existence and basic properties
            await self._check_file_properties(dubbed_file, results)
            
            # Check audio quality
            await self._check_audio_quality(original_file, dubbed_file, results)
            
            # Check video quality (if applicable)
            if self._is_video_file(dubbed_file):
                await self._check_video_quality(original_file, dubbed_file, results)
            
            # Check synchronization
            await self._check_synchronization(original_file, dubbed_file, results)
            
        except Exception as e:
            self.logger.error(f"Quality validation failed: {e}")
            results["valid"] = False
            results["issues"].append(f"Validation error: {str(e)}")
        
        return results
    
    async def _check_file_properties(self, file_path: str, results: Dict):
        """Check basic file properties"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            results["valid"] = False
            results["issues"].append("Output file does not exist")
            return
        
        file_size = file_path.stat().st_size
        results["metrics"]["file_size_mb"] = file_size / (1024 * 1024)
        
        if file_size == 0:
            results["valid"] = False
            results["issues"].append("Output file is empty")
        elif file_size < 1024:  # Less than 1KB
            results["issues"].append("Output file is very small, may be corrupted")
    
    async def _check_audio_quality(self, original_file: str, dubbed_file: str, results: Dict):
        """Check audio quality metrics"""
        try:
            from ...core.utils import AudioUtils
            audio_utils = AudioUtils()
            
            # Get duration comparison
            original_duration = await audio_utils.get_audio_duration(original_file)
            dubbed_duration = await audio_utils.get_audio_duration(dubbed_file)
            
            results["metrics"]["original_duration"] = original_duration
            results["metrics"]["dubbed_duration"] = dubbed_duration
            
            duration_diff = abs(original_duration - dubbed_duration)
            duration_ratio = duration_diff / original_duration if original_duration > 0 else 0
            
            results["metrics"]["duration_difference"] = duration_diff
            results["metrics"]["duration_ratio"] = duration_ratio
            
            # Check if duration difference is significant
            if duration_ratio > 0.1:  # More than 10% difference
                results["issues"].append(f"Significant duration difference: {duration_diff:.2f}s")
            elif duration_ratio > 0.05:  # More than 5% difference
                results["recommendations"].append("Consider adjusting speech rate for better timing")
            
        except Exception as e:
            self.logger.warning(f"Audio quality check failed: {e}")
            results["issues"].append("Could not analyze audio quality")
    
    async def _check_video_quality(self, original_file: str, dubbed_file: str, results: Dict):
        """Check video quality metrics"""
        try:
            from ...core.utils import VideoUtils
            video_utils = VideoUtils()
            
            # Get video info
            original_info = await video_utils.get_video_info(original_file)
            dubbed_info = await video_utils.get_video_info(dubbed_file)
            
            # Compare resolutions
            orig_streams = original_info.get("streams", [])
            dubbed_streams = dubbed_info.get("streams", [])
            
            orig_video = next((s for s in orig_streams if s.get("codec_type") == "video"), None)
            dubbed_video = next((s for s in dubbed_streams if s.get("codec_type") == "video"), None)
            
            if orig_video and dubbed_video:
                orig_res = (orig_video.get("width", 0), orig_video.get("height", 0))
                dubbed_res = (dubbed_video.get("width", 0), dubbed_video.get("height", 0))
                
                results["metrics"]["original_resolution"] = orig_res
                results["metrics"]["dubbed_resolution"] = dubbed_res
                
                if orig_res != dubbed_res:
                    results["recommendations"].append(
                        f"Resolution changed from {orig_res} to {dubbed_res}"
                    )
            
        except Exception as e:
            self.logger.warning(f"Video quality check failed: {e}")
            results["issues"].append("Could not analyze video quality")
    
    async def _check_synchronization(self, original_file: str, dubbed_file: str, results: Dict):
        """Check audio-video synchronization"""
        # This is a placeholder for more advanced sync checking
        # In practice, this could analyze lip-sync accuracy, timing alignment, etc.
        
        results["metrics"]["sync_check"] = "basic"
        results["recommendations"].append("Manual review recommended for sync quality")
    
    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video file"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        return Path(file_path).suffix.lower() in video_extensions
    
    async def generate_quality_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable quality report"""
        report = []
        report.append("=== Dubbing Quality Report ===\n")
        
        # Overall status
        status = "✅ PASSED" if validation_results["valid"] else "❌ FAILED"
        report.append(f"Overall Status: {status}\n")
        
        # Issues
        if validation_results["issues"]:
            report.append("Issues Found:")
            for issue in validation_results["issues"]:
                report.append(f"  ❌ {issue}")
            report.append("")
        
        # Metrics
        if validation_results["metrics"]:
            report.append("Quality Metrics:")
            for metric, value in validation_results["metrics"].items():
                if isinstance(value, float):
                    report.append(f"  📊 {metric}: {value:.2f}")
                else:
                    report.append(f"  📊 {metric}: {value}")
            report.append("")
        
        # Recommendations
        if validation_results["recommendations"]:
            report.append("Recommendations:")
            for rec in validation_results["recommendations"]:
                report.append(f"  💡 {rec}")
            report.append("")
        
        return "\n".join(report)