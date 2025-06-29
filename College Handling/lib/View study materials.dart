import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

void main() {
  runApp(const ViewStudyMaterials());
}

class ViewStudyMaterials extends StatelessWidget {
  const ViewStudyMaterials({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Study Materials',
      theme: ThemeData(
        primaryColor: Colors.blue,
        hintColor: Colors.orange,
        fontFamily: 'Roboto',
      ),
      home: const ViewStudyMaterialsPage(title: 'View Study Materials'),
    );
  }
}

class ViewStudyMaterialsPage extends StatefulWidget {
  const ViewStudyMaterialsPage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<ViewStudyMaterialsPage> createState() => _ViewStudyMaterialsPageState();
}

class _ViewStudyMaterialsPageState extends State<ViewStudyMaterialsPage> {
  List<String> id_ = [];
  List<String> upload_file_ = [];
  List<String> subject_ = [];

  @override
  void initState() {
    super.initState();
    viewStudyMaterials();
  }

  Future<void> viewStudyMaterials() async {
    List<String> id = [];
    List<String> upload_file = [];
    List<String> subject = [];

    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewstudymeterial/';

      var data = await http.post(Uri.parse(url), body: {
        'lid': lid
      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        upload_file.add(sh.getString('imageurl').toString() + arr[i]['upload file'].toString());
        subject.add(arr[i]['subject name'].toString());
      }

      setState(() {
        id_ = id;
        upload_file_ = upload_file;
        subject_ = subject;
      });

      print(statuss);
    } catch (e) {
      print("Error: $e");
    }
  }

  // Future<bool> launchUrl(Uri url) async {
  //   if (await canLaunch(url.toString())) {
  //     await launch(url.toString());
  //     return true;
  //   } else {
  //     return false;
  //   }
  // }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: ListView.builder(
        itemCount: id_.length,
        itemBuilder: (BuildContext context, int index) {
          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Card(
              elevation: 8,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ListTile(
                    title: Text(
                      'Subject: ${subject_[index]}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      'ID: ${id_[index]}',
                      style: TextStyle(
                        color: Colors.grey,
                      ),
                    ),
                    trailing: ElevatedButton(
                      onPressed: () async {
                        if (!await launchUrl(Uri.parse(upload_file_[index]))) {
                          throw Exception('could not load');
                        }
                      },
                      child: Text("Download"),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
