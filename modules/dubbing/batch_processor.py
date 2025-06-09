"""
Batch processing for multiple dubbing tasks
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import concurrent.futures


class BatchProcessor:
    """Batch processor for multiple dubbing tasks"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    async def process_directory(self, input_dir: str, output_dir: str,
                               target_language: str, **kwargs) -> Dict[str, Any]:
        """
        Process all video files in a directory
        
        Args:
            input_dir: Directory containing input videos
            output_dir: Directory for output videos
            target_language: Target language for dubbing
            **kwargs: Additional dubbing parameters
            
        Returns:
            Dict with batch processing results
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find video files
        video_files = self._find_video_files(input_path)
        
        if not video_files:
            return {
                "status": "completed",
                "total_files": 0,
                "processed": 0,
                "failed": 0,
                "results": []
            }
        
        self.logger.info(f"Found {len(video_files)} video files to process")
        
        # Process files in batches
        results = await self._process_files_parallel(
            video_files, output_path, target_language, **kwargs
        )
        
        # Compile summary
        summary = {
            "status": "completed",
            "total_files": len(video_files),
            "processed": sum(1 for r in results if r["status"] == "completed"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }
        
        return summary
    
    def _find_video_files(self, directory: Path) -> List[Path]:
        """Find all video files in directory"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(directory.glob(f"*{ext}"))
            video_files.extend(directory.glob(f"*{ext.upper()}"))
        
        return sorted(video_files)
    
    async def _process_files_parallel(self, video_files: List[Path], 
                                    output_dir: Path, target_language: str,
                                    **kwargs) -> List[Dict[str, Any]]:
        """Process files in parallel"""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_single_file(video_file: Path) -> Dict[str, Any]:
            async with semaphore:
                return await self._process_single_file(
                    video_file, output_dir, target_language, **kwargs
                )
        
        # Create tasks for all files
        tasks = [process_single_file(video_file) for video_file in video_files]
        
        # Process with progress tracking
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            result = await task
            results.append(result)
            
            status = "✅" if result["status"] == "completed" else "❌"
            self.logger.info(f"[{i}/{len(video_files)}] {status} {result['input_file']}")
        
        return results
    
    async def _process_single_file(self, video_file: Path, output_dir: Path,
                                 target_language: str, **kwargs) -> Dict[str, Any]:
        """Process a single video file"""
        output_file = output_dir / f"{video_file.stem}_dubbed{video_file.suffix}"
        
        try:
            from ...core import DubbingPipeline, DubbingTask
            
            pipeline = DubbingPipeline()
            task = DubbingTask(
                input_file=str(video_file),
                output_file=str(output_file),
                target_language=target_language,
                **kwargs
            )
            
            result = await pipeline.process_task(task)
            
            return {
                "input_file": str(video_file),
                "output_file": str(output_file),
                "status": result["status"],
                "error": result.get("error"),
                "processing_time": result.get("processing_time"),
                "steps": result.get("steps", {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process {video_file}: {e}")
            return {
                "input_file": str(video_file),
                "output_file": str(output_file),
                "status": "failed",
                "error": str(e)
            }
    
    async def process_file_list(self, file_list: List[str], output_dir: str,
                               target_language: str, **kwargs) -> Dict[str, Any]:
        """
        Process a specific list of files
        
        Args:
            file_list: List of input file paths
            output_dir: Directory for output files
            target_language: Target language for dubbing
            **kwargs: Additional dubbing parameters
            
        Returns:
            Dict with batch processing results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        video_files = [Path(f) for f in file_list if Path(f).exists()]
        
        if not video_files:
            return {
                "status": "completed",
                "total_files": 0,
                "processed": 0,
                "failed": 0,
                "results": []
            }
        
        results = await self._process_files_parallel(
            video_files, output_path, target_language, **kwargs
        )
        
        summary = {
            "status": "completed",
            "total_files": len(video_files),
            "processed": sum(1 for r in results if r["status"] == "completed"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }
        
        return summary