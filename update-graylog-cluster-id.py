#!/usr/bin/env python3

import argparse
from pymongo import MongoClient

DEFAULTS = {
    "mongodb_host": "localhost",
    "mongodb_port": 27017,
    "mongodb_username": "",
    "mongodb_password": "",
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        "-H",
        help="MongoDB hostname",
        type=str,
        default=DEFAULTS["mongodb_host"],
    )
    parser.add_argument(
        "--port", "-p", help="MongoDB port", type=int, default=DEFAULTS["mongodb_port"]
    )
    parser.add_argument(
        "--username",
        "-U",
        help="MongoDB username",
        type=str,
        default=DEFAULTS["mongodb_username"],
    )
    parser.add_argument(
        "--password",
        "-P",
        help="MongoDB password",
        type=str,
        default=DEFAULTS["mongodb_password"],
    )
    parser.add_argument(
        "--cluster-id", help="Graylog Cluster ID", required=True, type=str
    )
    args = parser.parse_args()
    return args


def get_mongodb_collection(host, port, username, password):
    if username != "" and password != "":
        mongodb_url = f"mongodb://{username}:{password}@{host}:{port}"
    else:
        mongodb_url = f"mongodb://{host}:{port}"
    mongo_client = MongoClient(mongodb_url)
    db = mongo_client.graylog
    return db["cluster_config"]


def get_cluster_id(collection):
    return collection.find_one({"type": "org.graylog2.plugin.cluster.ClusterId"})[
        "payload"
    ]["cluster_id"]


def update_cluster_id(collection, cluster_id):
    print(f"Setting Graylog Cluster ID to {cluster_id}")
    result = collection.find_one_and_update(
        {"type": "org.graylog2.plugin.cluster.ClusterId"},
        {"$set": {"payload": {"cluster_id": cluster_id}}},
    )
    return True if result["payload"]["cluster_id"] == cluster_id else False


def main():
    args = parse_args()
    collection = get_mongodb_collection(
        args.host, args.port, args.username, args.password
    )
    if get_cluster_id(collection) != args.cluster_id:
        if update_cluster_id(collection, args.cluster_id) == True:
            print("Cluster ID successfully updated!")


if __name__ == "__main__":
    main()
