import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/home.dart';

void main() {
  runApp(const Viewnotification());
}

class Viewnotification extends StatelessWidget {
  const Viewnotification({Key? key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Announcement',
      theme: ThemeData(
        primaryColor: Colors.blueAccent,
        hintColor: Colors.orange,
        fontFamily: 'Roboto',
      ),
      home: const ViewnotificationPage(title: 'View Announcement'),
    );
  }
}

class ViewnotificationPage extends StatefulWidget {
  const ViewnotificationPage({Key? key, required this.title});

  final String title;

  @override
  State<ViewnotificationPage> createState() => _ViewnotificationPageState();
}

class _ViewnotificationPageState extends State<ViewnotificationPage> {
  late List<String> title_;
  late List<String> content_;

  @override
  void initState() {
    super.initState();
    title_ = [];
    content_ = [];
    Viewnotification();
  }

  Future<void> Viewnotification() async {
    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/viewnotification/';

      var data = await http.post(Uri.parse(url), body: {'lid': lid});
      var jsonData = json.decode(data.body);
      String statuss = jsonData['status'];

      var arr = jsonData["data"];

      for (int i = 0; i < arr.length; i++) {
        title_.add(arr[i]['title']);
        content_.add(arr[i]['content']);
      }

      setState(() {});

      print(statuss);
    } catch (e) {
      print("Error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.title,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView.builder(
        itemCount: title_.length,
        itemBuilder: (BuildContext context, int index) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: Card(
              elevation: 5,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15.0),
              ),
              child: ListTile(
                title: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Title: ${title_[index]}',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueAccent,
                      ),
                    ),
                    SizedBox(height: 8),
                    SizedBox(height: 8),
                    Text(
                      'notification: ${content_[index]}',
                      style: TextStyle(
                        color: Colors.black87,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
