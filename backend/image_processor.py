import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageStat
import imagehash
from typing import List, Tuple, Dict
import os


class ImageProcessor:
    """AI-powered image quality assessment and processing"""
    
    def __init__(self, quality_threshold: float = 0.6, blur_threshold: float = 100, 
                 duplicate_threshold: int = 5):
        self.quality_threshold = quality_threshold
        self.blur_threshold = blur_threshold
        self.duplicate_threshold = duplicate_threshold
        self.image_hashes = {}
    
    def assess_quality(self, image_path: str) -> Dict[str, float]:
        """
        Assess image quality based on multiple metrics
        Returns dict with quality scores
        """
        # Load image with OpenCV
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            return {
                "error": "Could not load image",
                "quality_score": 0.0,
                "sharpness_score": 0.0,
                "face_clarity_score": 0.0,
                "composition_score": 0.0,
                "brightness_score": 0.0,
                "contrast_score": 0.0,
                "face_count": 0,
                "is_blur": True,
                "is_high_quality": False
            }
        
        # Load with PIL for additional analysis
        img_pil = Image.open(image_path)
        
        # Calculate base metrics
        sharpness = self._calculate_sharpness(img_cv)
        brightness = self._calculate_brightness(img_pil)
        contrast = self._calculate_contrast(img_pil)
        
        # Detect faces for specialized analysis
        faces = self._detect_faces_raw(img_cv)
        face_count = len(faces)
        
        # Specialized face metrics
        face_clarity = self._calculate_face_clarity(img_cv, faces)
        composition_score = self._calculate_composition_score(img_cv, faces)
        
        # Normalize scores to 0-1 range
        sharpness_score = min(sharpness / 500, 1.0)
        brightness_score = self._normalize_brightness(brightness)
        contrast_score = min(contrast / 80, 1.0)
        
        # Calculate overall quality score (weighted average)
        # Weights: Sharpness(30%), Face Clarity(25%), Composition(15%), Brightness(15%), Contrast(15%)
        quality_score = (
            sharpness_score * 0.3 +
            face_clarity * 0.25 +
            composition_score * 0.15 +
            brightness_score * 0.15 +
            contrast_score * 0.15
        )
        
        return {
            "quality_score": round(float(quality_score), 3),
            "sharpness_score": round(float(sharpness_score), 3),
            "face_clarity_score": round(float(face_clarity), 3),
            "composition_score": round(float(composition_score), 3),
            "brightness_score": round(float(brightness_score), 3),
            "contrast_score": round(float(contrast_score), 3),
            "face_count": face_count,
            "is_blur": bool(sharpness < self.blur_threshold),
            "is_high_quality": bool(quality_score >= self.quality_threshold)
        }
    
    def _calculate_sharpness(self, img_cv: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance
        Higher values indicate sharper images
        """
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var
    
    def _calculate_brightness(self, img_pil: Image.Image) -> float:
        """
        Calculate average brightness (luminance)
        Returns value between 0-255
        """
        greyscale = img_pil.convert('L')
        stat = ImageStat.Stat(greyscale)
        return stat.mean[0]
    
    def _normalize_brightness(self, brightness: float) -> float:
        """
        Normalize brightness to 0-1 score
        Optimal brightness is around 128 (middle gray)
        """
        # Penalize images that are too dark or too bright
        optimal = 128
        deviation = abs(brightness - optimal)
        score = 1.0 - (deviation / optimal)
        return max(0.0, score)
    
    def _calculate_contrast(self, img_pil: Image.Image) -> float:
        """
        Calculate image contrast using standard deviation
        Higher values indicate more contrast
        """
        greyscale = img_pil.convert('L')
        stat = ImageStat.Stat(greyscale)
        return stat.stddev[0]
    
    def _detect_faces_raw(self, img_cv: np.ndarray) -> List:
        """Helper for internal face detection during assessment"""
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces

    def _calculate_face_clarity(self, img_cv: np.ndarray, faces: List) -> float:
        """Calculate sharpness specifically in face regions"""
        if len(faces) == 0:
            return 0.5  # Neutral score if no faces
        
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        face_scores = []
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            if face_roi.size > 0:
                score = cv2.Laplacian(face_roi, cv2.CV_64F).var()
                face_scores.append(min(score / 400, 1.0))
        
        return np.mean(face_scores) if face_scores else 0.5

    def _calculate_composition_score(self, img_cv: np.ndarray, faces: List) -> float:
        """Check if subjects are positioned effectively (Rule of Thirds approximation)"""
        if len(faces) == 0:
            return 0.7  # High baseline for scenic/empty shots if they are sharp
        
        h, w = img_cv.shape[:2]
        center_x, center_y = w / 2, h / 2
        
        # Good composition often has subjects off-center but balanced
        # Or centered for portraits. We give a boost for intentional positioning.
        composition_scores = []
        for (fx, fy, fw, fh) in faces:
            face_center_x = fx + fw / 2
            face_center_y = fy + fh / 2
            
            # Distance from "power points" (1/3 and 2/3 coordinates)
            points = [(w/3, h/3), (2*w/3, h/3), (w/3, 2*h/3), (2*w/3, 2*h/3), (w/2, h/2)]
            min_dist = min([np.sqrt((face_center_x - px)**2 + (face_center_y - py)**2) for px, py in points])
            
            # Higher score for being closer to a power point or center
            score = 1.0 - (min_dist / (np.sqrt(w**2 + h**2) / 4))
            composition_scores.append(max(0.0, score))
            
        return np.mean(composition_scores)
    
    def detect_duplicates(self, image_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Detect duplicate images using perceptual hashing
        Returns list of (original, duplicate) tuples
        """
        duplicates = []
        hashes = {}
        
        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                img_hash = imagehash.average_hash(img)
                
                # Check for similar hashes
                for existing_path, existing_hash in hashes.items():
                    if img_hash - existing_hash <= self.duplicate_threshold:
                        duplicates.append((existing_path, img_path))
                        break
                else:
                    hashes[img_path] = img_hash
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        return duplicates
    
    def enhance_image(self, image_path: str, output_path: str = None, fast: bool = False) -> str:
        """
        Apply professional enhancements to image:
        - Noise reduction (fast mode: skipped or subtle)
        - White balance
        - Lighting balance (CLAHE)
        - Smart Sharpening
        """
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            # Avoid triple extensions if already enhanced
            if "_enhanced" in base:
                output_path = image_path
            else:
                output_path = f"{base}_enhanced{ext}"
        
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            return image_path
            
        # 1. Noise Reduction (Subtle)
        # fastNlMeansDenoisingColored is very slow, skip it in fast mode
        if not fast:
            img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 3, 3, 7, 21)
        
        # 2. Simple White Balance (Gray World)
        result = img_cv.astype(np.float32)
        avg_b = np.mean(result[:, :, 0])
        avg_g = np.mean(result[:, :, 1])
        avg_r = np.mean(result[:, :, 2])
        avg_gray = (avg_b + avg_g + avg_r) / 3
        # Avoid division by zero
        avg_b = max(avg_b, 0.001)
        avg_g = max(avg_g, 0.001)
        avg_r = max(avg_r, 0.001)
        
        result[:, :, 0] *= (avg_gray / avg_b)
        result[:, :, 1] *= (avg_gray / avg_g)
        result[:, :, 2] *= (avg_gray / avg_r)
        img_cv = np.clip(result, 0, 255).astype(np.uint8)
        
        # 3. Lighting Balance (CLAHE for local contrast/detail)
        lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        img_cv = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Convert to PIL for final tweaks and saving
        img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        
        # 4. Smart Multi-step Sharpen
        sharpness_level = self._calculate_sharpness(img_cv)
        if sharpness_level < 150:
            enhancer = ImageEnhance.Sharpness(img_pil)
            img_pil = enhancer.enhance(1.2)
        
        # Vitality boost (Saturation)
        enhancer = ImageEnhance.Color(img_pil)
        img_pil = enhancer.enhance(1.05)
        
        img_pil.save(output_path, quality=95, subsampling=0)
        return output_path
    
    def detect_faces(self, image_path: str) -> int:
        """
        Detect number of faces in image
        Returns count of faces detected
        """
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces)
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return 0
    
    def select_best_images(self, image_scores: List[Dict], max_count: int = 10) -> List[Dict]:
        """
        Select the best images based on quality scores
        Prioritizes high-quality, non-blurry, non-duplicate images
        """
        # Filter out blurry and duplicate images
        valid_images = [
            img for img in image_scores 
            if not img.get('is_blur', False) and not img.get('is_duplicate', False)
        ]
        
        # Sort by quality score (descending)
        sorted_images = sorted(
            valid_images, 
            key=lambda x: x.get('quality_score', 0), 
            reverse=True
        )
        
        # Return top N images
        return sorted_images[:max_count]
    
    def batch_process(self, image_paths: List[str]) -> Dict[str, any]:
        """
        Process multiple images in batch
        Returns comprehensive analysis
        """
        results = []
        
        # Assess quality for all images
        for img_path in image_paths:
            try:
                quality_metrics = self.assess_quality(img_path)
                quality_metrics['path'] = img_path
                quality_metrics['filename'] = os.path.basename(img_path)
                results.append(quality_metrics)
            except Exception as e:
                print(f"   [ERROR] Failed to process {img_path}: {e}")
                results.append({
                    "error": str(e),
                    "path": img_path,
                    "filename": os.path.basename(img_path),
                    "quality_score": 0.0,
                    "is_blur": True,
                    "is_duplicate": False,
                    "is_high_quality": False
                })
        
        # Detect duplicates
        duplicates = self.detect_duplicates(image_paths)
        duplicate_paths = set([dup[1] for dup in duplicates])
        
        # Mark duplicates in results
        for result in results:
            result['is_duplicate'] = result['path'] in duplicate_paths
        
        # Select best images
        best_images = self.select_best_images(results)
        
        return {
            'total_images': len(image_paths),
            'all_results': results,
            'duplicates': duplicates,
            'selected_images': best_images,
            'summary': {
                'total': len(image_paths),
                'high_quality': len([r for r in results if r.get('is_high_quality', False)]),
                'blurry': len([r for r in results if r.get('is_blur', False)]),
                'duplicates': len(duplicates),
                'selected': len(best_images)
            }
        }
