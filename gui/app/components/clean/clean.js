angular.module('librarian')
    .controller('CleanController', ['$scope', '$rootScope', '$http',
        function ($scope, $rootScope, $http) {
          'use strict';
          
            $scope.loading = true;

            $http({
                method: 'POST',
                url: '/',
                data: {
                    library_dir: $rootScope.libraryDir,
                    action: 'scan'
                }
            }).success(function(data, status, headers, config) {

                $scope.dupCount = data.count;
                $scope.duplicates = data.duplicates;

                // Remove button initialization
                $scope.removeButton = 'Remove duplicates';
                $scope.isProcessing = false;

                $scope.view = 'finished';

                $scope.loading = false;
            });

        }]);
