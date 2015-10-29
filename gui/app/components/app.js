/*global $:false */
/*global angular:false */
/*global console:false */

angular.module('librarian', ['ngRoute'])

.config([
    '$routeProvider',

    function($routeProvider)  {

      $routeProvider
          .when('/clean/', {
              templateUrl: '../static/components/clean/clean.html',
              controller: 'CleanController'
          })
          .when('/export', {
              templateUrl: '../static/components/export/export.html',
              controller: 'ExportController'
          })
          .when('/', {
              templateUrl: '../static/components/landing/landing.html',
              controller: 'LandingController'
          });
    }
  ])
.controller('HeaderController', [
    '$scope',
    '$location',
    '$http',
    '$rootScope',

    function($scope, $location, $http, $rootScope) {
      'use strict';

        var initialize = function() {
            $http({
                method: 'POST',
                url: '/',
                data: {
                    action: 'initialize'
                }
            }).success(function (data, status, headers, config) {
                if(data.status == "ok") {
                    $rootScope.error = false;
                    $rootScope.volumes = data.volumes;
                } else if (data.statur == "error") {
                    $rootScope.error = true;
                }
            });
        }

        $scope.goToHome = function() {
            if ($location.path() !== '/') {
                $location.path('/');
            }
        };

        $rootScope.checkTraktor = function() {
            initialize();
        }

        $scope.selectLibrary = function() {
            $http({
              method: 'POST',
              url: '/',
              data: {
                action: 'open_file_dialog',
                traktor_check: true
              }
            }).success(function (data) {

              if(data.status == "ok") {
                $rootScope.traktorDir = data.directory;
                initialize();
              } else if (data.status == "error") {
                $rootScope.error = true;
                $rootScope.errorMessage = data.message;
              }
            });
        }
    }
  ]);
