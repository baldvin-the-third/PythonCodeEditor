"""Configuration for supported programming languages"""
import re

SUPPORTED_LANGUAGES = {
    "python": {
        "name": "Python",
        "ace_mode": "python",
        "file_extension": ".py",
        "comment_prefix": "#",
        "execution_command": "python3",
        "features": {
            "syntax_highlighting": True,
            "code_completion": True,
            "execution": True,
            "formatting": True,
            "linting": True
        },
        "libraries": {
            "completion": "jedi",
            "formatting": "autopep8",
            "linting": "pylint"
        },
        "sample_code": '''def greet(name):
    """Greet someone with their name."""
    return f"Hello, {name}!"

# Example usage
if __name__ == "__main__":
    message = greet("World")
    print(message)
'''
    },
    "javascript": {
        "name": "JavaScript",
        "ace_mode": "javascript",
        "file_extension": ".js",
        "comment_prefix": "//",
        "execution_command": "node",
        "features": {
            "syntax_highlighting": True,
            "code_completion": True,
            "execution": True,
            "formatting": True,
            "linting": False
        },
        "libraries": {
            "completion": "tern",
            "formatting": "prettier",
            "linting": "eslint"
        },
        "sample_code": '''function greet(name) {
    return `Hello, ${name}!`;
}

// Example usage
const message = greet("World");
console.log(message);

// Array example
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log("Doubled:", doubled);
'''
    },
    "java": {
        "name": "Java",
        "ace_mode": "java",
        "file_extension": ".java",
        "comment_prefix": "//",
        "execution_command": "javac",
        "features": {
            "syntax_highlighting": True,
            "code_completion": False,
            "execution": True,
            "formatting": True,
            "linting": False
        },
        "libraries": {
            "completion": None,
            "formatting": "google-java-format",
            "linting": "checkstyle"
        },
        "sample_code": '''public class HelloWorld {
    public static void main(String[] args) {
        String name = "World";
        String message = greet(name);
        System.out.println(message);
        
        // Array example
        int[] numbers = {1, 2, 3, 4, 5};
        System.out.println("Sum: " + calculateSum(numbers));
    }
    
    public static String greet(String name) {
        return "Hello, " + name + "!";
    }
    
    public static int calculateSum(int[] numbers) {
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        return sum;
    }
}
'''
    },
    "cpp": {
        "name": "C++",
        "ace_mode": "c_cpp",
        "file_extension": ".cpp",
        "comment_prefix": "//",
        "execution_command": "g++",
        "features": {
            "syntax_highlighting": True,
            "code_completion": False,
            "execution": True,
            "formatting": True,
            "linting": False
        },
        "libraries": {
            "completion": "clangd",
            "formatting": "clang-format",
            "linting": "cppcheck"
        },
        "sample_code": '''#include <iostream>
#include <vector>
#include <string>
#include <numeric>

std::string greet(const std::string& name) {
    return "Hello, " + name + "!";
}

int calculateSum(const std::vector<int>& numbers) {
    return std::accumulate(numbers.begin(), numbers.end(), 0);
}

int main() {
    std::string name = "World";
    std::cout << greet(name) << std::endl;
    
    // Vector example
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    std::cout << "Sum: " << calculateSum(numbers) << std::endl;
    
    return 0;
}
'''
    }
}

# Language detection patterns
LANGUAGE_PATTERNS = {
    "python": [
        r"def\s+\w+\s*\(",
        r"import\s+\w+",
        r"from\s+\w+\s+import",
        r"print\s*\(",
        r"if\s+__name__\s*==\s*[\"']__main__[\"']:"
    ],
    "javascript": [
        r"function\s+\w+\s*\(",
        r"var\s+\w+\s*=",
        r"let\s+\w+\s*=",
        r"const\s+\w+\s*=",
        r"console\.log\s*\(",
        r"document\.",
        r"window\.",
        r"=>\s*{"
    ],
    "java": [
        r"public\s+class\s+\w+",
        r"public\s+static\s+void\s+main",
        r"System\.out\.println",
        r"import\s+java\.",
        r"@Override",
        r"private\s+\w+\s+\w+",
        r"public\s+\w+\s+\w+\s*\("
    ],
    "cpp": [
        r"#include\s*<\w+>",
        r"int\s+main\s*\(",
        r"std::",
        r"cout\s*<<",
        r"cin\s*>>",
        r"using\s+namespace\s+std",
        r"#include\s*<iostream>"
    ]
}

# Code templates for quick start
CODE_TEMPLATES = {
    "python": {
        "basic": '''# Python Basic Template
print("Hello, World!")
''',
        "function": '''def my_function(param):
    """Description of the function."""
    return param

# Call the function
result = my_function("test")
print(result)
''',
        "class": '''class MyClass:
    """A simple example class."""
    
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

# Usage
obj = MyClass("Hello")
print(obj.get_value())
'''
    },
    "javascript": {
        "basic": '''// JavaScript Basic Template
console.log("Hello, World!");
''',
        "function": '''function myFunction(param) {
    return param;
}

// Call the function
const result = myFunction("test");
console.log(result);
''',
        "class": '''class MyClass {
    constructor(value) {
        this.value = value;
    }
    
    getValue() {
        return this.value;
    }
}

// Usage
const obj = new MyClass("Hello");
console.log(obj.getValue());
'''
    },
    "java": {
        "basic": '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
''',
        "class": '''public class MyClass {
    private String value;
    
    public MyClass(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
    
    public static void main(String[] args) {
        MyClass obj = new MyClass("Hello");
        System.out.println(obj.getValue());
    }
}
'''
    },
    "cpp": {
        "basic": '''#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
''',
        "class": '''#include <iostream>
#include <string>

class MyClass {
private:
    std::string value;

public:
    MyClass(const std::string& val) : value(val) {}
    
    std::string getValue() const {
        return value;
    }
};

int main() {
    MyClass obj("Hello");
    std::cout << obj.getValue() << std::endl;
    return 0;
}
'''
    }
}

def get_language_config(language: str):
    """Get configuration for a specific language"""
    return SUPPORTED_LANGUAGES.get(language, {})

def get_supported_languages():
    """Get list of supported language names"""
    return list(SUPPORTED_LANGUAGES.keys())

def detect_language_from_code(code: str) -> str:
    """Detect language from code patterns"""
    if not code.strip():
        return "python"  # Default
    
    scores = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, code, re.IGNORECASE | re.MULTILINE))
            score += matches
        scores[lang] = score
    
    # Return language with highest score
    if scores:
        detected = max(scores.items(), key=lambda x: x[1])
        if detected[1] > 0:
            return detected[0]
    
    return "python"  # Default fallback

def get_code_template(language: str, template_type: str = "basic") -> str:
    """Get code template for a language"""
    templates = CODE_TEMPLATES.get(language, {})
    return templates.get(template_type, "")
