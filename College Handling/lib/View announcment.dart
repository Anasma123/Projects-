import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/home.dart';

void main() {
  runApp(const ViewAnnouncement());
}

class ViewAnnouncement extends StatelessWidget {
  const ViewAnnouncement({Key? key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Announcement',
      theme: ThemeData(
        primaryColor: Colors.blueAccent,
        hintColor: Colors.orange,
        fontFamily: 'Roboto',
      ),
      home: const ViewAnnouncementPage(title: 'View Announcement'),
    );
  }
}

class ViewAnnouncementPage extends StatefulWidget {
  const ViewAnnouncementPage({Key? key, required this.title});

  final String title;

  @override
  State<ViewAnnouncementPage> createState() => _ViewAnnouncementPageState();
}

class _ViewAnnouncementPageState extends State<ViewAnnouncementPage> {
  late List<String> title_;
  late List<String> date_;
  late List<String> announcement_;

  @override
  void initState() {
    super.initState();
    title_ = [];
    date_ = [];
    announcement_ = [];
    viewAnnouncement();
  }

  Future<void> viewAnnouncement() async {
    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewannouncment/';

      var data = await http.post(Uri.parse(url), body: {'lid': lid});
      var jsonData = json.decode(data.body);
      String statuss = jsonData['status'];

      var arr = jsonData["data"];

      for (int i = 0; i < arr.length; i++) {
        title_.add(arr[i]['title']);
        date_.add(arr[i]['date']);
        announcement_.add(arr[i]['description']);
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
                    Text('Date: ${date_[index]}'),
                    SizedBox(height: 8),
                    Text(
                      'Announcement: ${announcement_[index]}',
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
