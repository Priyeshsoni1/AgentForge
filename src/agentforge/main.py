import time

from agentforge.agent.graph import graph


def main():
    question = input("Enter Your Problem ?.......... ")

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    print("\nFinal Answer:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    start = time.time()

    main()

    end = time.time()

    print(f"\nTime: {end - start:.2f} seconds")