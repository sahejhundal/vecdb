import os
from dotenv import load_dotenv
import cohere
import json
from typing import List, Dict
from uuid import uuid4

load_dotenv()

co = cohere.Client(os.getenv('COHERE_API_KEY'))

def create_embedding(text: str) -> List[float]:
    try:
        response = co.embed(
            texts=[text],
            model='embed-english-v3.0',
            input_type='search_document'
        )
        return response.embeddings[0]
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None

def save_embeddings_to_file(documents: Dict[str, List[str]], output_file: str = "../server/embeddings.txt"):
    results = []
    
    for doc_title, chunks in documents.items():
        print(f"Processing document: {doc_title}")
        
        for chunk in chunks:
            embedding = create_embedding(chunk)
            if embedding:
                results.append({
                    "text": chunk,
                    "embedding": embedding,
                    "metadata": {
                        "document_title": doc_title
                    }
                })
                print(f"Generated embedding for chunk: {chunk[:50]}...")
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved {len(results)} embeddings from {len(documents)} documents to {output_file}")

# Sample documents with chunks
sample_documents = {
    "Artificial Intelligence": [
        "Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from data",
        "Deep learning is a type of machine learning based on artificial neural networks",
        "Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and human language",
        "Artificial neural networks are computing systems inspired by biological neural networks",
        "Computer vision enables machines to interpret and understand visual information from the world",
        "Reinforcement learning is a type of machine learning where agents learn to make decisions through trial and error",
        "Transfer learning allows models to leverage knowledge from one task to improve performance on another",
        "Generative AI models can create new content such as images, text, and music",
        "Explainable AI focuses on making machine learning models more transparent and interpretable",
        "Federated learning enables training AI models across multiple devices while preserving data privacy"
    ],
    
    "Cloud and Infrastructure": [
        "Cloud computing is the delivery of computing services over the internet",
        "Containerization is a lightweight alternative to full machine virtualization",
        "Docker simplifies application deployment using containerization",
        "Kubernetes is an open-source container orchestration platform",
        "Serverless computing allows developers to build applications without managing servers",
        "Infrastructure as Code (IaC) automates infrastructure provisioning and management",
        "Cloud-native applications are designed to run in cloud environments",
        "Edge computing brings computation and data storage closer to data sources",
        "Multi-cloud strategies use multiple cloud providers for different workloads",
        "Cloud security focuses on protecting cloud-based systems and data",
        "Auto-scaling automatically adjusts resources based on demand",
        "Cloud migration involves moving applications and data to cloud platforms"
    ],
    
    "Software Development": [
        "DevOps is a set of practices that combines software development and IT operations",
        "Agile methodology emphasizes iterative development and cross-functional collaboration",
        "Test-driven development writes tests before implementing features",
        "Version control systems track and manage changes to software code",
        "Continuous Integration ensures automated testing of code changes",
        "Code review is a systematic examination of source code to find and fix mistakes",
        "Refactoring improves code structure without changing its behavior",
        "Design patterns are reusable solutions to common software design problems",
        "API design principles guide the creation of effective interfaces",
        "Software architecture defines the fundamental structure of a system",
        "Technical debt represents the implied cost of additional rework",
        "Code documentation helps developers understand and maintain software"
    ],
    
    "Data Storage and Processing": [
        "Vector databases are specialized databases designed to store and search vector embeddings efficiently",
        "Database indexing improves the speed of data retrieval operations",
        "SQL is a standard language for managing relational databases",
        "NoSQL databases provide flexible schemas for unstructured data",
        "Data warehousing centralizes data from multiple sources for analysis",
        "Data lakes store raw data in its native format",
        "ETL processes extract, transform, and load data between systems",
        "Data streaming enables real-time processing of continuous data",
        "Data governance ensures data quality and security",
        "Data modeling defines the structure and relationships of data",
        "Data replication creates copies of data for backup and availability",
        "Data partitioning improves performance by dividing data into smaller parts"
    ],
    
    "System Architecture": [
        "Microservices architecture breaks down applications into small, independent services",
        "RESTful APIs are architectural constraints that enable standardized communication between systems",
        "GraphQL is a query language for APIs that gives clients precise data control",
        "Message queues enable asynchronous communication between services",
        "Distributed systems are computing environments where components are spread across networks",
        "Event-driven architecture uses events to trigger and communicate between services",
        "Service mesh provides infrastructure for service-to-service communication",
        "Circuit breakers prevent cascading failures in distributed systems",
        "Load balancing distributes network traffic across multiple servers",
        "Caching improves performance by storing frequently accessed data",
        "API gateways manage and secure API access",
        "Event sourcing stores all changes to application state as a sequence of events"
    ],

    "Cybersecurity": [
        "Encryption protects data by converting it into a secure format",
        "Authentication verifies the identity of users and systems",
        "Authorization controls access to resources based on permissions",
        "Firewalls monitor and control network traffic",
        "Intrusion detection systems identify potential security threats",
        "Penetration testing simulates attacks to find vulnerabilities",
        "Security information and event management (SIEM) centralizes security monitoring",
        "Zero trust security assumes no implicit trust in any user or system",
        "Vulnerability management identifies and addresses security weaknesses",
        "Security compliance ensures adherence to security standards and regulations",
        "Threat modeling identifies potential security threats and mitigations",
        "Security automation reduces manual security tasks"
    ],

    "Web Development": [
        "Progressive Web Apps (PWAs) provide app-like experiences on the web",
        "Single Page Applications (SPAs) load content dynamically without page refreshes",
        "Web Components create reusable custom elements for web applications",
        "Responsive design ensures websites work well on all devices",
        "Web accessibility makes websites usable by people with disabilities",
        "Web performance optimization improves loading speed and user experience",
        "Web security protects against common web vulnerabilities",
        "Web APIs enable communication between web services",
        "Web standards ensure consistent behavior across browsers",
        "Web frameworks provide tools and libraries for web development",
        "Web testing ensures quality and functionality of web applications",
        "Web deployment automates the process of releasing web applications"
    ],

    "Mobile Development": [
        "Native apps are built specifically for a particular platform",
        "Cross-platform development creates apps that work on multiple platforms",
        "Mobile UI/UX design focuses on creating intuitive mobile interfaces",
        "Mobile app testing ensures quality across different devices",
        "Mobile app security protects user data and app functionality",
        "Mobile app performance optimization improves speed and efficiency",
        "Mobile app analytics track user behavior and app usage",
        "Mobile app monetization strategies generate revenue from apps",
        "Mobile app distribution manages app deployment to stores",
        "Mobile app maintenance keeps apps updated and bug-free",
        "Mobile app architecture organizes code and components",
        "Mobile app accessibility makes apps usable by everyone"
    ]
}

if __name__ == "__main__":
    save_embeddings_to_file(sample_documents)