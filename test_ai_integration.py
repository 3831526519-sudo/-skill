import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Set a dummy API key so that the DeepSeek API call will fail and we test the fallback
os.environ['DEEPSEEK_API_KEY'] = 'dummy_key_for_testing'

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import generate_essay_with_deepseek, post_process_essay, generate_essay_fallback

class TestAIGeneration(unittest.TestCase):
    
    def test_generate_essay_fallback(self):
        """Test the fallback function"""
        topic = "测试主题"
        word_count = 500
        structure = 'three-part'
        result = generate_essay_fallback(topic, word_count, structure)
        self.assertIsInstance(result, str)
        self.assertIn(topic, result)
        self.assertIn("引言", result)
        self.assertIn("结论", result)
        print("Fallback test passed")
    
    def test_post_process_essay(self):
        """Test the post processing function"""
        topic = "测试主题"
        text = "这是一个测试。"
        target_word_count = 100
        # Too short, should add conclusion
        processed = post_process_essay(text, topic, target_word_count)
        self.assertIn("总之", processed)
        print("Post-process short text test passed")
        
        # Too long, should truncate
        long_text = "。".join(["句子" + str(i) for i in range(50)])  # 50 sentences
        processed_long = post_process_essay(long_text, topic, 100)  # target 100 chars
        self.assertLess(len(processed_long), len(long_text))
        print("Post-process long text test passed")
        
        # Normal text, should return similar
        normal_text = "这是一个正常长度的测试文本。" * 10
        processed_normal = post_process_essay(normal_text, topic, 200)
        self.assertEqual(processed_normal, normal_text)  # Should be unchanged
        print("Post-process normal text test passed")
    
    @patch('app.OpenAI')
    def test_generate_essay_with_deepseek_success(self, mock_openai_class):
        """Test the AI generation when API call succeeds"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "这是由AI生成的测试内容。"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call the function
        result = generate_essay_with_deepseek("测试主题", 500, 'three-part', False)
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertEqual(result, "这是由AI生成的测试内容。")
        mock_client.chat.completions.create.assert_called_once()
        print("AI generation success test passed")
    
    @patch('app.OpenAI')
    def test_generate_essay_with_deepseek_failure(self, mock_openai_class):
        """Test the AI generation when API call fails (should fallback)"""
        # Setup mock to raise an exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Call the function
        result = generate_essay_with_deepseek("测试主题", 500, 'three-part', False)
        
        # Assertions - should have fallen back to the template
        self.assertIsInstance(result, str)
        self.assertIn("测试主题", result)
        self.assertIn("引言", result)
        print("AI generation failure (fallback) test passed")

if __name__ == '__main__':
    unittest.main()