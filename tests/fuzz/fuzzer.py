import subprocess
import random
import string
import sys
import os
import time

def generate_random_orhun_code(length):
    # Orhun keywords and operators to increase chance of hitting parser logic
    keywords = ["yazdır", "olsun", "eğer", "ise", "değilse", "doğru", "yanlış", 
                "tekrarla", "kez", "sor", "işlev", "döndür", "sürece", "tip", 
                "yeni", "benim", "deneme", "yakala", "kır", "devam", "ust",
                "her", "için", "içinde", "paralel", "yap"]
    operators = ["+", "-", "*", "/", "=", "==", "!=", "<", ">", "(", ")", "{", "}", "[", "]", ",", ".", ":"]
    
    # Mix of random chars and keywords
    chars = string.ascii_letters + string.digits + string.punctuation + " \n\t"
    
    code = ""
    while len(code) < length:
        choice = random.choice(["char", "keyword", "operator", "newline"])
        if choice == "char":
            code += random.choice(chars)
        elif choice == "keyword":
            code += " " + random.choice(keywords) + " "
        elif choice == "operator":
            code += random.choice(operators)
        elif choice == "newline":
            code += "\n"
            
    return code

def generate_nested_code(depth):
    # Generates deeply nested structures to test stack overflow
    code = ""
    openers = ["(", "[", "{", "eğer ", "işlev f", "sürece ", "her x içinde [1, 2, 3]"]
    closers = {
        "(": ")", 
        "[": "]", 
        "{": "}", 
        "eğer ": ":\n    ", # if requires indentation or block
        "işlev f": "():\n    ", 
        "sürece ": " 1:\n    ",
        "her x içinde [1, 2, 3]": ":\n    "
    }
    
    structure = []
    
    for _ in range(depth):
        op = random.choice(openers)
        if op in ["eğer ", "işlev f", "sürece ", "her x içinde [1, 2, 3]"]:
            code += op + closers[op]
        else:
            code += op
            structure.append(closers[op])
            
    code += " " * 10 # Some content
    
    # Close them
    while structure:
        code += structure.pop()
        
    return code

def run_fuzzer(executable_path, iterations=1000, artifacts_dir="build/fuzz"):
    print(f"Starting fuzzing on {executable_path} for {iterations} iterations...")
    
    crashes_dir = os.path.join(artifacts_dir, "crashes")
    temp_dir = os.path.join(artifacts_dir, "tmp")
    os.makedirs(crashes_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "current_fuzz_input.oh")
    
    start_time = time.time()
    crashes = 0
    
    for i in range(iterations):
        # 80% random, 20% nested stress
        if random.random() < 0.2:
            depth = random.randint(100, 2000) # Deep nesting
            code = generate_nested_code(depth)
        else:
            length = random.randint(10, 1000)
            code = generate_random_orhun_code(length)
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            # Run the process
            result = subprocess.run(
                [executable_path, temp_file],
                capture_output=True,
                text=True,
                timeout=2 # Timeout to prevent infinite loops from freezing the fuzzer
            )
            
            # Check for crash (Exit code other than 0 or 1 usually indicates a crash/segfault)
            # 3221225477 is 0xC0000005 (Access Violation)
            if result.returncode not in [0, 1] and result.returncode != 3221225786: # 3221225786 is Ctrl+C
                print(f"CRASH DETECTED at iteration {i}! Exit code: {result.returncode}")
                crash_file = os.path.join(crashes_dir, f"crash_{int(time.time())}_{i}.oh")
                with open(crash_file, "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"Saved crash input to {crash_file}")
                crashes += 1
                
        except subprocess.TimeoutExpired:
            # Timeout is somewhat expected with random code (infinite loops), so we ignore it
            pass
        except Exception as e:
            print(f"Fuzzer error at iteration {i}: {e}")
            
        if (i + 1) % 100 == 0:
            elapsed = time.time() - start_time
            print(f"Progress: {i + 1}/{iterations} ({crashes} crashes found) - {elapsed:.2f}s")

    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except OSError:
            pass

    print(f"Fuzzing complete. Total crashes: {crashes}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fuzzer.py <path_to_orhun_executable>")
        sys.exit(1)
        
    exe_path = sys.argv[1]
    run_fuzzer(exe_path, iterations=2000) # Default to 2000 for smoke test
