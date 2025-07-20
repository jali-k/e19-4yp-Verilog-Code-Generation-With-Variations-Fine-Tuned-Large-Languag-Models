#!/usr/bin/env python3
"""
Quick test of bias removal in code generator
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_bias_removal():
    """Test that bias has been removed from the code generator"""
    
    print('🎯 BIAS REMOVAL TEST')
    print('=' * 30)
    
    try:
        from xform_rag.code_generator import CodeGenerator
        from xform_rag.config import RAGConfig
        
        config = RAGConfig()
        generator = CodeGenerator(config)
        
        # Test the unbiased fix method with wire-to-reg request
        test_code = '''#!/usr/bin/env python3
import sys
# TODO: Add transformation logic here
def main():
    pass'''
        
        print('Testing wire-to-reg transformation (previously biased)...')
        fixed_code = generator._fix_generated_code(test_code, 'wire to reg transformation')
        
        print(f'Original code length: {len(test_code)} chars')
        print(f'Fixed code length: {len(fixed_code)} chars')
        print(f'Contains TODO: {"TODO" in fixed_code}')
        print(f'Contains wire-specific logic: {"wire_signals" in fixed_code}')
        print(f'Contains hardcoded fixes: {"Convert specific signal" in fixed_code}')
        
        # Test with module rename (also previously biased)
        print('\nTesting module rename transformation (previously biased)...')
        fixed_code2 = generator._fix_generated_code(test_code, 'module rename transformation')
        
        print(f'Module rename fixed length: {len(fixed_code2)} chars')
        print(f'Wire vs Module code length difference: {abs(len(fixed_code) - len(fixed_code2))} chars')
        
        # Check for bias indicators
        bias_indicators = 0
        if 'TODO' in fixed_code:
            bias_indicators += 1
            print('❌ TODO comments not removed')
        if 'wire_signals' in fixed_code:
            bias_indicators += 1
            print('❌ Wire-specific logic still present')
        if 'Convert specific signal' in fixed_code:
            bias_indicators += 1
            print('❌ Hardcoded transformation logic still present')
        if abs(len(fixed_code) - len(fixed_code2)) > 100:
            bias_indicators += 1
            print('❌ Significant difference between transformation types')
        
        if bias_indicators == 0:
            print('\n✅ SUCCESS: Bias removal working correctly!')
            print('All transformations now get equal treatment.')
            return True
        else:
            print(f'\n❌ FAIL: {bias_indicators} bias indicators still present')
            return False
            
    except Exception as e:
        print(f'❌ Error testing bias removal: {e}')
        return False

if __name__ == "__main__":
    success = test_bias_removal()
    sys.exit(0 if success else 1)
